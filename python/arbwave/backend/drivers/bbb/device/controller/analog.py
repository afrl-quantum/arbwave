#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""

import bbb.ltc2668

import Pyro4

from .base import Device as Base
from . import _main_controller_loop as Main
from .bbb_pyro import ANALOG_PYRO4_PORT as PYRO4_PORT
from .analog_details import Details

SPANS         = bbb.ltc2668.instruction.device_instructions.Span.OUTPUT_RANGE
SPANS_reverse = bbb.ltc2668.instruction.device_instructions.Span.RANGE_VAL_TO_STR

class Device(Base, bbb.ltc2668.Device, Details):
  # need to export a number of things from the device
  # generic items
  exec_waveform    = Pyro4.expose(bbb.ltc2668.Device.exec_waveform)
  waitfor_waveform = Pyro4.expose(bbb.ltc2668.Device.waitfor_waveform)
  stop             = Pyro4.expose(bbb.ltc2668.Device.stop)
  reset            = Pyro4.expose(bbb.ltc2668.Device.reset)
  flush_input      = Pyro4.expose(bbb.ltc2668.Device.flush_input)
  set_output       = Pyro4.expose(Details.set_output)
  # analog specific items
  update_src       = Pyro4.expose(bbb.ltc2668.Device.update_src)
  get_minimum_period=Pyro4.expose(bbb.ltc2668.Device.get_minimum_period)
  set_waveforms    = Pyro4.expose(Details.set_waveforms)

  # make it easier to be called from Details.set_output
  base_set_output  =              bbb.ltc2668.Device.set_output


  """
  Analog Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    # this opens connection to firmware and also resets device; the system clock
    # parameters will have to be set up.
    super(Device,self).__init__(hostid, 'analog')
    self.assert_sw_fw_compatibility()
    self.reset()
    self.powered = True # turn the power on


  @Pyro4.expose
  def set_monitor(self, channel, enable):
    super(Device,self).set_monitor(channel=channel, enable=enable)


  @Pyro4.expose
  def get_monitor(self):
    D = super(Device,self).get_monitor().dict()
    D.pop('read')
    return dict(D)


  @Pyro4.expose
  def set_chip_config(self, disable_thermal_protection):
    super(Device,self).set_config(
      disable_thermal_protection=disable_thermal_protection)


  @Pyro4.expose
  def get_chip_config(self):
    D = super(Device,self).get_config().dict()
    D.pop('read')
    return dict(D)


  @Pyro4.expose
  def set_toggled(self, toggled):
    super(Device,self).set_tgb(toggled=toggled)


  @Pyro4.expose
  def get_toggled(self):
    return super(Device,self).get_tgb().toggled


  @Pyro4.expose
  def set_toggle_select(self, channels):
    super(Device,self).set_tsr(channels=channels)


  @Pyro4.expose
  def get_toggle_select(self):
    return super(Device,self).get_tsr().channels


  @Pyro4.expose
  def get_span_values(self):
    """
    Return a list of string representations for all possible PLL charge pump
    values.
    """
    return list(SPANS.keys())


  @Pyro4.expose
  def set_span(self, span, channel=None, all=False):
    if all:
      super(Device,self).set_span(span=SPANS[span].val, all=True)
    elif channel is None:
      raise RuntimeError('bbb.analog: must specify all=True or channel=<num> '
                         'for setting channel span')
    else:
      super(Device,self).set_span(span=SPANS[span].val, channel=channel)


  @Pyro4.expose
  def get_span(self, channel):
    return SPANS_reverse[super(Device,self).get_span(channel=channel).span]


  def volts_to_DAC(self, channel, data):
    """
    Takes data in physical units and converts it to 16-bit data that the ltc2668
    device needs.

    This version does *not* use numpy and thus does not work with arrays.
    """
    rng = SPANS[self.get_span(channel)]
    maxdata = (1 << 16) - 1
    return int(
      min(max((data - rng.min) * (maxdata / (rng.max - rng.min)), 0), maxdata)
    )


  def load_waveform(self, wlen, channel_bits, flat_waveform):
    self.set_waveform_length(wlen, channel_bits)
    self.waveform[:] = flat_waveform
 

def main():
  import sys

  Main.main(Device, PYRO4_PORT)
  sys.exit()
