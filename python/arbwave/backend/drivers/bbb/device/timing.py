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


  def __init__(self, *a, **kw):
    super(Device,self).__init__(*a, **kw)
    self.digital_channels = [
      channels.Digital('{}/{}'.format(self,i), self) for i in xrange(4)
    ]
    self.timing_channels = [
      channels.Timing('{}/{}'.format(self,i), self) for i in xrange(4)
    ]
    self.timing_channels.append(
      channels.AM335x_L3_CLK('{}/InternalClock'.format(self))
    )
    self.config = None


  def close(self):
    super(Device,self).close()
    self.config = None


  @cached.property
  def possible_clock_sources(self):
    return [
      '{dev}/InternalClock'.format(dev=self),
    ]


  def get_config_template(self):
    """
    Create the configuration template (the set of possible configuration
    parameters and their allowed values).

    :return: the configuration template
    """

    if self.proxy is None:
      self.open()

    D = Dict()

    config = {
      'trigger' : {
        'enable': {
          'value': self.proxy.triggered,
          'type': bool,
          'range': None,
        },
        'setup_time' : {
          'value' : self.proxy.start_delay * 5*units.ns,
          'type'  : float,
          'range' : float_range(3*5*units.ns, ((2**48)-1)*5*units.ns, step=5*units.ns),
        },
        'retrigger': {
          'value': self.proxy.retrigger,
          'type': bool,
          'range': None,
        },
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
    valid_keys = set(['trigger', 'clock'])
    assert set(config.keys()).issubset(valid_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)
    valid_trigger_keys = set(['enable', 'setup_time', 'retrigger'])
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
    if self.config['trigger'] != trg_config:
      if self.config['enable'] != trg_config['enable']:
        self.proxy.triggered = trg_config['enable']['value']

      if self.config['setup_time'] != trg_config['setup_time']:
        self.proxy.start_delay = \
          int(trg_config['setup_time']['value'] / (5*units.ns))

      if self.config['retrigger'] != trg_config['retrigger']:
        self.proxy.retrigger = trg_config['retrigger']['value']

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
    if not isinstance(values, dict):
      values = dict(values)

    value = 0
    for ch, val in values.iteritems():
      if 8 <= ch <= 9:
        ch += 6 # channel 8 and 9 are bits 14 and 15
      elif ch < 0 or ch > 9:
        raise RuntimeError('bbb.timing: invalid channel number [{}]'.format(ch))

      if val:
        value |=   1 << ch
      else:
        value &= ~(1 << ch)
    self.proxy.data = value


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
    if self.connection:
      #self.connection.set_waveforms(
      #  waveforms, clock_transitions, t_max, continuous)
      pass
    self.is_continuous = continuous
