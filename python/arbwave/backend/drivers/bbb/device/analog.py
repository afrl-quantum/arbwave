# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Analog logical device driver for the BeagleBone Black using AFRL
firmware/hardware.
"""

import copy
import itertools
from logging import debug
from physical import unit
import time

from .....tools.float_range import float_range
from .....tools.dict import Dict
from .....tools import cached
from .....tools.signal_graphs import nearest_terminal
from .. import channels
from .base import Device as Base


class Device(Base):
  """
  Analog logical device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """
  _NCHAN = 16 # LTC2668 has 16 channels


  def __init__(self, *a, **kw):
    super(Device,self).__init__(*a, **kw)
    self.channels = [
      channels.Analog('{}/{}'.format(self,i), self) for i in range(self._NCHAN)
    ]
    self.configured_channels = set()
    self.config = None
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

    if not self.isopen():
      self.open(take_ownership=True)

    monitor = self.guard_proxy.get_monitor()
    chip_config = self.guard_proxy.get_chip_config()
    toggle_channels = self.guard_proxy.get_toggle_select()

    config = {
      'monitor': {
        'enable': {
          'value': monitor['enable'],
          'type' : bool,
          'range': None,
        },
        'channel': {
          'value': monitor['channel'],
          'type' : int,
          'range': range(self._NCHAN),
        },
      },
      'thermal_protection': {
        'value': not chip_config['disable_thermal_protection'],
        'type' : bool,
        'range': None,
      },
      'toggle': {
        'state': {
          'value': self.guard_proxy.get_toggled(),
          'type' : bool,
          'range': None,
        },
        'select': {},
      },
      'span': {},
      'clock': {
        'value': '',
        'type': str,
        'range': list(self.possible_clock_sources.keys()),
      },
    }

    # add per-channel info:
    #   - toggle bits
    #   - span info
    for ch in range(self._NCHAN):
      chname = str(ch)

      config['toggle']['select'][chname] = {
        'value': bool(toggle_channels & (1 << ch)),
        'type' : bool,
        'range': None,
      }

      config['span'][chname] = {
        'value': self.guard_proxy.get_span(channel=ch),
        'type' : str,
        'range': self.guard_proxy.get_span_values(),
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

    Analog device uses channel info to configure what value is returned for the
    get_min_period function (depends on the number of channels configured).
    """
    debug('bbb.Device(%s).set_config(config=%s, channels=%s, signal_graph=%s)',
          self, config, channels, signal_graph)
    valid_keys = set([
      'monitor', 'thermal_protection', 'toggle', 'span', 'clock',
    ])
    assert set(config.keys()).issubset(valid_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)

    valid_monitor_keys = set(['enable', 'channel'])
    assert set(config['monitor'].keys()).issubset(valid_monitor_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)

    valid_toggle_keys = set(['state', 'select'])
    assert set(config['toggle'].keys()).issubset(valid_toggle_keys), \
      'bbb.Device({}): Unknown configuration keys for AFRL/BeagleBone Black' \
      .format(self)

    if self.config is None:
      # If this is not set yet, this is the first time accessing device
      self.get_config_template()

    if self.configured_channels != channels.keys():
      # first set new minium-period for this DDS
      if len(self.configured_channels) != len(channels):
        self.min_period = \
          self.guard_proxy.get_minimum_period(max(1,len(channels))) * 5*unit.ns

      # TODO:
      # We *may* want to implement this where the unused channels get set to a
      # predefined value (like 0*V).  This predefined value could also be
      # defined by the user in the configuration settings for this device.
      #
      # # we need to turn off channels that have been disabled: set output = 0.0V
      # old_chans = {
      #   ch : 0.0
      #   for ch in (self.configured_channels - channels.keys())
      # }
      # if old_chans:
      #   debug('bbb.Device(%s): resetting old Analog channels (%s)',
      #         self, old_chans)
      #   self.guard_proxy.set_output(old_chans)

      self.configured_channels = set(channels)

    if self.config == config:
      return

    if self.config['monitor'] != config['monitor']:
      self.guard_proxy.set_monitor(channel=config['monitor']['channel']['value'],
                                   enable=config['monitor']['enable']['value'])

    if self.config['thermal_protection'] != config['thermal_protection']:
      self.guard_proxy.set_chip_config(config['thermal_protection']['value'])

    if self.config['toggle']['state'] != config['toggle']['state']:
      self.guard_proxy.set_toggled(config['toggle']['state']['value'])

    if self.config['toggle']['select'] != config['toggle']['select']:
      toggle_channels = 0
      for ch in range(self._NCHAN):
        if config['toggle']['select'][str(ch)]['value']:
          toggle_channels |= (1 << ch)
      # now give bit array as toggle select register value
      self.guard_proxy.set_toggled(toggle_channels)

    if self.config['span'] != config['span']:
      for ch in range(self._NCHAN):
        chname = str(ch)

        if self.config['span'][chname] != config['span'][chname]:
          self.guard_proxy.set_span(channel=ch,
                                    span=config['span'][chname]['value'])


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

        self.guard_proxy.update_src = update_src
    except:
      # We'll set this to something that will never be an input
      self.config['clock']['value'] = 'clock selection error'
      raise


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

    if not isinstance(values, dict):
      values = dict(values)

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
    if self.isopen():
      transitions = sorted(
        clock_transitions[ self.config['clock']['value'] ]['transitions'])

      self.guard_proxy.set_waveforms(waveforms, transitions)
