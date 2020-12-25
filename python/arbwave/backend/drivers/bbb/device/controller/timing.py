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
  set_output       = Pyro4.expose(Details.set_output)
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


def main():
  import sys

  Main.main(Device, PYRO4_PORT)
  sys.exit()
