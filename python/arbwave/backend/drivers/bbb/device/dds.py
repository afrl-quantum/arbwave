# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
DDS logical device driver for the BeagleBone Black using AFRL firmware/hardware.
"""

import copy
import itertools
from logging import debug
import numpy as np
from physical import units
import time

from .....tools.float_range import float_range
from .....tools.dict import Dict
from .....tools import cached
from .....tools.signal_graphs import nearest_terminal
from .. import channels
from .base import Device as Base


class Device(Base):
  """
  DDS logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """


  def __init__(self, *a, **kw):
    super(Device,self).__init__(*a, **kw)
    self.channels = [
      channels.DDS('{}/{}'.format(self,i), self) for i in range(4)
    ]
    self.config = None
    self.number_configured_channels = 0
    self.min_period = None


  def close(self):
    super(Device,self).close()
    self.config = None


  @cached.property
  def possible_clock_sources(self):
    return {
      '{}/update'.format(self) : 'update',
      '{}/timing/0'.format(str(self).rpartition('/')[0]) : 'timing/0',
    }


  def get_routeable_backplane_signals(self):
    return [
      channels.Backplane('External/', ['{}/update'.format(self)]),
    ]


  def get_config_template(self):
    """
    Create the configuration template (the set of possible configuration
    parameters and their allowed values).

    :return: the configuration template
    """

    if self.proxy is None:
      self.open()

    D = Dict(self.proxy.get_sysclk_float())
    refclk_src = self.proxy.refclk_src

    config = {
      'sysclk': {
        'value': D.sysclk,
        'type' : float,
        'range': float_range(1e6, 500e6),
      },
      'refclk': {
        'source': {
          'value': refclk_src,
          'type' : str,
          'range': ['tcxo', 'refclk'],
        },
        'frequency' : {
          'value': D.refclk,
          'type' : float,
          'range': [50e6] if refclk_src == 'tcxo' else float_range(1e6, 100e6),
          'doreload' : True, # reload the range everytime we need it
        },
      },
      'pll_chargepump': {
        'value': D.charge_pump,
        'type' : str,
        'range': self.proxy.get_charge_pump_values(),
      },
      'clock': {
        'value': '',
        'type': str,
        'range': list(self.possible_clock_sources.keys()),
      },
    }

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.config = copy.deepcopy(config)
    return config

  def set_config(self, config, channels, signal_graph):
    """
    Set the internal configuration for the board. This
    does not include the sequence specification or the backplane routing.

    :param config: the configuration dictionary to be applied, compare
                   get_config_template()
    :param channels: Dictionary of channels configured for this device.  Each
                   value returned is actually a dictionary including max, min
                   output values for the channel and also the order of the
                   channel in the channel list on the gui.
    :param signal_graph: directed graph of signal routing

    DDS device uses channel info to configure what value is returned for the
    get_min_period function (depends on the number of channels configured).
    """
    debug('bbb.Device(%s).set_config(config=%s, channels=%s, signal_graph=%s)',
          self, config, channels, signal_graph)
    valid_keys = set([
      'sysclk', 'refclk', 'pll_chargepump', 'clock'
    ])
    assert set(config.keys()).issubset(valid_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)
    valid_refclk_keys = set(['source', 'frequency'])
    assert set(config['refclk'].keys()).issubset(valid_refclk_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.get_config_template()

    if self.number_configured_channels != len(channels):
      self.number_configured_channels = len(channels)
      self.min_period = max(
          self.proxy.get_minimum_period(self.number_configured_channels)
              .values()
        ) * 5*units.ns

    if self.config == config:
      return

    if (self.config['sysclk'] != config['sysclk'] or
        self.config['refclk']['frequency'] != config['refclk']['frequency'] or
        self.config['pll_chargepump'] != config['pll_chargepump']):
      self.proxy.set_sysclk_float(config['refclk']['frequency']['value'],
                                  config['sysclk']['value'],
                                  config['pll_chargepump']['value'])

    if self.config['refclk']['source'] != config['refclk']['source']:
      self.proxy.refclk_src = config['refclk']['source']['value']

    # keep a copy of the config given to us
    old_config = self.config
    self.config = copy.deepcopy(config)

    # set the clock.  Have to map the actual clock source to the clock terminal
    # (one of the items in self.possible_clock_sources) that needs to be
    # connected.
    if not self.config['clock']['value']:
      # set it to something that will never be an input
      self.config['clock']['value'] = 'No clock selected'
      raise UserWarning('bbb.Device({}): please assign clock'.format(self))

    try:
      if old_config['clock'] !=  self.config['clock']:
        clock_terminal = nearest_terminal(self.config['clock']['value'],
                                          set(self.possible_clock_sources),
                                          signal_graph)
        update_src = self.possible_clock_sources[clock_terminal]
        debug('bbb.Device(%s).update_src = (terminal=%s, internal=%s)',
              self, clock_terminal, update_src)

        self.proxy.update_src = update_src
    finally:
      # We'll set this to something that will never be an input
      self.config['clock']['value'] = 'clock selection error'


  def get_min_period(self):
    return self.min_period


  def get_output_channels(self):
    return self.channels


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    debug('bbb.Device(%s).set_output(values=%s)', self, values)
    self.proxy.set_output(values)


  def set_waveforms_impl(self, waveforms, clock_transitions, t_max):
    """
    Set the output waveforms for the AFRL/BeagleBone Black device.

    :param waveforms:
      a dict('channel': {<wfe-path>: (<encoding>, [(t1, val1), (t2, val2)])})
                      (see gui/plotter/digital.py for format)
                      where wfe-path means waveform element path, referring to
                      the unique identifier of the specific waveform element a
                      particular set of values refers to.
    :param clock_transitions: a dict('channel': { 'dt': dt,
                              'transitions': iterable})
                              (see processor/engine/compute.py for format)
    :param t_max: the maximum duration of any channel in units of time.
    """
    if self.proxy:
      self.proxy.set_waveforms(waveforms, self.number_configured_channels)
