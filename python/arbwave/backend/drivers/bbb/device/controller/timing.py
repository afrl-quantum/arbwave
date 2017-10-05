#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


from itertools import izip
from physical import unit
import bbb.timing

from base import Device as Base


class Device(Base, bbb.timing.Device):
  """
  Timing Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'timing')
    self.assert_sw_fw_compatibility()
    self.reset()


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    if not isinstance(values, dict):
      values = dict(values)

    value = 0
    for ch, val in values.iteritems():
      ch = int(ch)
      if 8 <= ch <= 9:
        ch += 6 # channel 8 and 9 are bits 14 and 15
      elif ch < 0 or ch > 9:
        raise RuntimeError('{}: invalid channel number [{}]'.format(self, ch))

      if val:
        value |=   1 << ch
      else:
        value &= ~(1 << ch)
    self.data = value


  def set_waveforms(self, waveforms, clock_transitions, t_max):
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
    """
    if set(waveforms.iterkeys()).intersection(clock_transitions.iterkeys()):
      raise RuntimeError('bbb::timing channels cannot be used as clocks and ' \
                         'digital output simultaneously')

    transition_map = self._compile_transition_map(waveforms, clock_transitions, t_max)
    self.set_waveform_size(len(transition_map) - 1) # one is a dummy at the end
    self._load_transitions(transition_map)


  def _compile_transition_map(self, waveforms, clock_transitions, t_max):
    """
    Convert the input waveforms from being channel-indexed to being
    timestamp-indexed.

    :param waveforms: the dict of waveforms from the processor engine
    :param clock_transitions: the dict of required clock transitions from the
                              processor engine
    :param t_max: the total duration of the sequence

    :return: a dict(timestamp: {channel: value})
    """
    unit_time = 5*unit.ns
    transition_map = {}

    # find how time is scaled for our clock
    base_clk_cfg = clock_transitions.pop('InternalClock')
    base_clk = int(base_clk_cfg['dt'] / unit_time)

    # first reformat the waveforms: this is straightforward
    for channel, groups in waveforms.iteritems():
      for _, (encoding, transitions) in groups.iteritems():
        # encoding is currently ignored (i.e. not defined) for digital
        # channel data
        for timestamp, value in transitions:
          transition_map.setdefault(timestamp*base_clk, {})[channel] = value

    # then add the clock transitions
    for channel, cfg in clock_transitions.iteritems():
      # calculate the time in units if `unit_time`
      period = int(round(cfg['dt'] / unit_time))
      for edge in cfg['transitions']:
        edge *= period # rescale from dt to `unit_time` units

        # add clock edges to the transtion map
        # FIXME: it would not be too hard to support inverted channels...
        transition_map.setdefault(edge, {})[channel] = True
        transition_map.setdefault(edge + period/2, {})[channel] = False

    # add a dummy transition to the end to finish the sequence
    # convert to #minimum_period#s, then to unit_time
    ts_max = int(round(t_max / (self.minimum_period * unit_time))) \
           * self.minimum_period
    ts_max = max([max(transition_map.iterkeys())+self.minimum_period, ts_max])
    transition_map[ts_max] = {}

    return transition_map


  def _load_transitions(self, transition_map):
    """
    Load all transitions into the waveform data memory.

    Note that this captures the current manual settings for all channels
    that are not controlled by the waveform specification. If the manual
    value changes the sequence must be recompiled to preserve the new
    manual value.

    :param transition_map: a dict(timestamp: {channel: value})
                           The last transition (i.e. the one with the largest
                           value) does not have any data and only serves to
                           create the delay for the last real transition.
    """
    # sort and format the transitions
    TM = sorted(transition_map.iterkeys())
    data = self.data
    for wi, t0, t1 in izip(self.waveform, TM[:-1], TM[1:]):
      for ch, value in transition_map[t0].iteritems():
        ch = int(ch)
        if 8 <= ch <= 9:
          ch += 6 # channel 8 and 9 are bits 14 and 15
        elif ch < 0 or ch > 9:
          raise RuntimeError('{}: invalid channel number [{}]'.format(self, ch))

        if value:
          data |=  (1 << ch)
        else:
          data &= ~(1 << ch)
      wi.delay = t1 - t0
      wi.data = data



if __name__ == '__main__':
  import sys, _main_controller_loop as Main

  Main.main(Device)
  sys.exit()
