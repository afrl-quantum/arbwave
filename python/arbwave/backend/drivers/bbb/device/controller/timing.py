#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


if __name__ == '__main__':
  import _main_controller_loop as Main
  import arbwave.backend.drivers.bbb.device.controller.timing as timing

  Main.main(timing.Device)
  sys.exit()




import bbb.timing

from .....tools import cached
from ....device import BBB_PYRO_GROUP, format_objectId
from .. import channels
from .base import Device as Base


class Device(Base, bbb.timing.Device):
  """
  Timing Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'dds', bbb.timing.Device)
