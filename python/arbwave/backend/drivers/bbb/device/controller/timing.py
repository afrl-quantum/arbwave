#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


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


if __name__ == '__main__':
  import sys, _main_controller_loop as Main

  Main.main(Device)
  sys.exit()
