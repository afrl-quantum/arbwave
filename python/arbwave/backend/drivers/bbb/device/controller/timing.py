#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


import bbb.timing

import Pyro4

from .base import Device as Base
from . import _main_controller_loop as Main
from .bbb_pyro import TIMING_PYRO4_PORT as PYRO4_PORT
from .timing_details import Details


class Device(Base, bbb.timing.Device, Details):
  # need to export a number of things from the device
  # generic items
  exec_waveform    = Pyro4.expose(bbb.timing.Device.exec_waveform)
  waitfor_waveform = Pyro4.expose(bbb.timing.Device.waitfor_waveform)
  stop             = Pyro4.expose(bbb.timing.Device.stop)
  reset            = Pyro4.expose(bbb.timing.Device.reset)
  flush_input      = Pyro4.expose(bbb.timing.Device.flush_input)
  # timing specific items
  triggered        = Pyro4.expose(bbb.timing.Device.triggered)
  retrigger        = Pyro4.expose(bbb.timing.Device.retrigger)
  start_delay      = Pyro4.expose(bbb.timing.Device.start_delay)
  trigger_level    = Pyro4.expose(bbb.timing.Device.trigger_level)
  trigger_pull     = Pyro4.expose(bbb.timing.Device.trigger_pull)
  set_waveforms    = Pyro4.expose(Details.set_waveforms)

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


  @Pyro4.expose
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
    for ch, val in values.items():
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
    TM = sorted(transition_map.keys())
    data = self.data
    for wi, t0, t1 in zip(self.waveform, TM[:-1], TM[1:]):
      for ch, value in transition_map[t0].items():
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


def main():
  import sys

  Main.main(Device, PYRO4_PORT)
  sys.exit()
