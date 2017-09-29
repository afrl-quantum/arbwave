#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


if __name__ == '__main__':
  import _main_controller_loop as Main
  import arbwave.backend.drivers.bbb.device.controller.dds as dds

  Main.main(dds.Device)
  sys.exit()




import bbb.ad9959

from .....tools import cached
from ....device import BBB_PYRO_GROUP, format_objectId
from .. import channels
from .base import Device as Base


class Device(Base, bbb.ad9959.Device):
  """
  DDS Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'dds', bbb.ad9959.Device)

    self.powered = True # turn the power on


  def set_sysclk(self, refclk, sysclk, charge_pump):
    refclk_MHz = refclk / 1e6 # must be in MHz
    sysclk_MHz = sysclk / 1e6 # must be in MHz
    charge_pump = bbb.ad9959.regs.FR1.CHARGE_PUMP['_'+charge_pump]
    super(Device,self).set_sysclk(refclk,_MHz, sysclk_MHz, charge_pump)


  def get_sysclk(self):
    D = super(Device,self).get_sysclk()
    D.sysclk = D.pop('sysclk_MHz') * 1e6
    D.refclk = D.pop('refclk_MHz') * 1e6
    # convert the charge_pump value into a nice string representation, but drop
    # the '_' prefix
    D.charge_pump = bbb.ad9959.regs.FR1.CHARGE_PUMP.reverse()[D.charge_pump][1:]
    # convert this to standard dict to more easily get across Pyro boundaries
    return dict(D)


  def get_charge_pump_values(self):
    """
    Return a list of string representations for all possible PLL charge pump
    values.
    """
    # remove the '_'_ prefix
    return tuple(v[1:] for v in bbb.ad9959.regs.FR1.CHARGE_PUMP.iterkeys())
