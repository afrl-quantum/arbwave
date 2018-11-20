# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Timing logical device driver for the BeagleBone Black using AFRL
firmware/hardware.
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
  Timing logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  # there are 10 channels with channels 0:7 corresponding to bits 0:7 and
  # channels 8:9 corresponding to bits 14:15.
  N_CHANNELS = 10

  def __init__(self, *a, **kw):
    super(Device,self).__init__(*a, **kw)
    self.digital_channels = [
      channels.Digital('{}/{}'.format(self,i), dev=self)
      for i in range(self.N_CHANNELS)
    ]
    self.timing_channels = [
      channels.Timing('{}/{}'.format(self,i), dev=self)
      for i in range(self.N_CHANNELS)
    ]
    self.timing_channels.append(
      channels.AM335x_L3_CLK('{}/InternalClock'.format(self), dev=self)
    )
    self.signals = [
      channels.Backplane('{}/{}'.format(self,i), ['External/'])
      for i in range(self.N_CHANNELS)
    ]
    self.config = None
    self.clocks = None


  def close(self):
    super(Device,self).close()
    self.config = None


  @cached.property
  def possible_clock_sources(self):
    return [
      '{dev}/InternalClock'.format(dev=self),
    ]


  def get_routeable_backplane_signals(self):
    return self.signals


  def get_config_template(self):
    """
    Create the configuration template (the set of possible configuration
    parameters and their allowed values).

    :return: the configuration template
    """

    if not self.isopen():
      self.open(take_ownership=True)

    D = Dict()

    config = {
      'trigger' : {
        'enable': {
          'value': self.guard_proxy.triggered,
          'type': bool,
          'range': None,
        },
        'retrigger': {
          'value': self.guard_proxy.retrigger,
          'type': bool,
          'range': None,
        },
        'level': {
          'value': 'low',
          'type': str,
          'range': ('high', 'low'),
        },
        'pull': {
          'value': 'down',
          'type': str,
          'range': ('down', 'up'),
        },
      },
      'start_delay' : {
        'value' : self.guard_proxy.start_delay * 5*units.ns,
        'type'  : float,
        'range' : float_range(3*5*units.ns, ((2**48)-1)*5*units.ns, step=5*units.ns),
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

    Timing device ignores channels at this point.
    """
    debug('bbb.Device(%s).set_config(config=%s, channels=%s, signal_graph=%s)',
          self, config, channels, signal_graph)
    valid_keys = set(['trigger', 'start_delay', 'clock'])
    assert set(config.keys()).issubset(valid_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)
    valid_trigger_keys = set(['enable', 'retrigger', 'level', 'pull'])
    assert set(config['trigger'].keys()).issubset(valid_trigger_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone ' \
                       'Black timing trigger' \
      .format(self)

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.config = self.get_config_template()

    if self.config == config:
      return

    trg_config = config['trigger']
    my_trg_config = self.config['trigger']
    if self.config['trigger'] != trg_config:
      if my_trg_config['enable'] != trg_config['enable']:
        self.guard_proxy.triggered = trg_config['enable']['value']

      if my_trg_config['retrigger'] != trg_config['retrigger']:
        self.guard_proxy.retrigger = trg_config['retrigger']['value']

      if my_trg_config['level'] != trg_config['level']:
        self.guard_proxy.trigger_level = trg_config['level']['value']

      if my_trg_config['pull'] != trg_config['pull']:
        self.guard_proxy.trigger_pull = trg_config['pull']['value']

    if self.config['start_delay'] != config['start_delay']:
      self.guard_proxy.start_delay = \
        int(config['start_delay']['value'] / (5*units.ns))


    # We don't really have to respond to the clock setting (for now, no hardware
    # to configure for this change)

    # finally, keep a copy of the config given to us
    self.config = copy.deepcopy(config)


  def set_clocks(self, clocks):
    """
    Set which clock is controlling the board.

    :param clocks: a dict of {'clock/path': config_dict }
    """
    debug('bbb.Device(%s).set_clocks(clocks=%s)', self, clocks)
    if self.clocks == clocks:
      return
    self.clocks = copy.deepcopy(clocks)


  def set_signals(self, signals):
    debug('bbb.Device(%s).set_signals(signals=%s)', self, signals)
    # for now, we only have timing/* --> External/* routes, for which we don't
    # have to do anything particular


  def get_output_channels(self):
    return self.digital_channels


  def get_timing_channels(self):
    return self.timing_channels


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    debug('bbb.Device(%s).set_output(values=%s)', self, values)
    self.guard_proxy.set_output(values)


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
    used_clocks_set = set(clock_transitions.keys())
    if not used_clocks_set.issubset(self.clocks.keys()):
      undefed_clocks = used_clocks_set - set(self.clocks.keys())
      raise RuntimeError(
        'got clock transitions for channels not defined as clocks ({})' \
        .format(undefed_clocks)
      )

    if self.isopen():
      self.guard_proxy.set_waveforms(waveforms, clock_transitions, t_max)
