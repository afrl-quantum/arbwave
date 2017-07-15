# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device driver for the BeagleBone Black using AFRL firmware/hardware.
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
from .. import channels
from .base import Device as Base


class Device(Base):
  """
  The Logical Device for a single instance of the BeagleBone Black DDS device
  using AFRL firmware/hardware.
  """


  def __init__(self, *a, **kw):
    super(Device,self).__init__(*a, **kw)
    self.channels = [
      channels.DDS('{}/{}'.format(self,i), self) for i in xrange(4)
    ]
    self.config = None


  def close(self):
    super(Device,self).close()
    self.config = None


  @cached.property
  def possible_clock_sources(self):
    return [
      '{}/ClockIn'.format(self),
      '{}/pru0/r30_0'.format(self.hostid),
    ]


  def get_routeable_backplane_signals(self):
    return [
      channels.Backplane('External/', ['{}/ClockIn'.format(self)]),
    ]


  def get_config_template(self):
    """
    Create the configuration template (the set of possible configuration
    parameters and their allowed values).

    :return: the configuration template
    """

    if self.proxy is None:
      self.open()

    D = Dict(self.proxy.get_sysclk())

    config = {
      'sysclk': {
        'value': D.sysclk,
        'type' : float,
        'range': float_range(1e6, 500e6),
      },
      'has_crystal_refclk': {
        'value': D.has_crystal_refclk,
        'type' : bool,
        'range': None,
      },
      'refclk': {
        'value': D.refclk,
        'type' : float,
        'range': float_range(1e6, 100e6) if not D.has_crystal_refclk \
            else float_range(20e6, 30e6),
        'doreload' : True, # reload the range everytime we need it
      },
      'pll_chargepump': {
        'value': D.charge_pump,
        'type' : str,
        'range': self.proxy.get_charge_pump_values(),
      },
      'clock': {
        'value': '',
        'type': str,
        'range': self.possible_clock_sources,
        'doreload' : True, # reload the range everytime we need it
      },
    }

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.config = config
    return config

  def set_config(self, config):
    """
    Set the internal configuration for the board. This
    does not include the sequence specification or the backplane routing.

    :param config: the configuration dictionary to be applied, compare
                   get_config_template()
    """
    debug('bbb.Device(%s).set_config(config=%s)', self, config)
    valid_keys = set([
      'sysclk', 'has_crystal_refclk', 'refclk', 'pll_chargepump', 'clock'
    ])
    assert set(config.keys()).issubset(valid_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.config = self.get_config_template()

    if self.config == config:
      return

    if (self.config['sysclk'] != config['sysclk'] or
        self.config['has_crystal_refclk'] != config['has_crystal_refclk'] or
        self.config['refclk'] != config['refclk'] or
        self.config['pll_chargepump'] != config['pll_chargepump']):
      self.proxy.set_sysclk(config['refclk']['value'],
                            config['sysclk']['value'],
                            config['pll_chargepump']['value'],
                            config['has_crystal_refclk']['value'])
        

    # We don't really have to respond to the clock setting (for now, no hardware
    # to configure for this change)

    # finally, keep a copy of the config given to us
    self.config = copy.deepcopy(config)


  def get_output_channels(self):
    return self.channels


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
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
    :param t_max: the maximum duration of any channel
    :param continuous: bool of continuous or single-shot mode
    """
    debug('bbb.Device(%s).set_waveforms(waveforms=%s, clock_transitions=%s, ' \
          't_max=%s, continuous=%s)',
          self, waveforms, clock_transitions, t_max, continuous)
    if self.proxy:
      self.proxy.set_waveforms(
        waveforms, clock_transitions, t_max, continuous)
    self.is_continuous = continuous
