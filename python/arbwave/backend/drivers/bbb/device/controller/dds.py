#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


import bbb.ad9959

from base import Device as Base

CHARGE_PUMP = bbb.Dict(bbb.ad9959.regs.FR1.CHARGE_PUMP)
CHARGE_PUMP.pop('Default')

class Device(Base, bbb.ad9959.Device):
  """
  DDS Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'dds')
    self.assert_sw_fw_compatibility()
    self.reset()
    self.powered = True # turn the power on


  def set_sysclk_float(self, refclk, sysclk, charge_pump):
    refclk_MHz = int(refclk / 1e6) # must be in MHz
    sysclk_MHz = int(sysclk / 1e6) # must be in MHz
    charge_pump = CHARGE_PUMP['_'+charge_pump]
    super(Device,self).set_sysclk(refclk_MHz, sysclk_MHz, charge_pump)


  def get_sysclk_float(self):
    D = super(Device,self).get_sysclk()
    D.sysclk = D.pop('sysclk_MHz') * 1e6
    D.refclk = D.pop('refclk_MHz') * 1e6
    # convert the charge_pump value into a nice string representation, but drop
    # the '_' prefix
    D.charge_pump = CHARGE_PUMP.reverse()[D.charge_pump][1:]
    # convert this to standard dict to more easily get across Pyro boundaries
    return dict(D)


  def get_charge_pump_values(self):
    """
    Return a list of string representations for all possible PLL charge pump
    values.
    """
    # remove the '_'_ prefix
    return tuple(v[1:] for v in CHARGE_PUMP.iterkeys())


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

    for ch, val in values.iteritems():
      ch = int(ch)
      assert 0 <= ch <= 3, \
        '{}.set_output:  invalid channel number [{}]'.format(self, ch)
      self.set_frequency(val, 1 << ch)


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
    :param continuous: bool of continuous or single-shot mode
    """
    raise RuntimeError(
      'bbb.Device({}): does not implement waveforms'.format(self))


if __name__ == '__main__':
  import sys, _main_controller_loop as Main

  Main.main(Device)
  sys.exit()
