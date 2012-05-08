# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from ...capabilities import *
import channels
import device

def get_devices():
  retval = list()
  for i in [
    'ni/dev0/ao',
    'ni/dev0/ao',
    'ni/dev1',
    'viewpoint/0',
  ]: retval.append( device.Device(i) )
  return retval

def get_analog_channels():
  retval = list()
  for i in [
    'ni/dev0/ao0',
    'ni/dev0/ao1',
    'ni/dev0/ao2',
    'ni/dev0/ao3',
  ]: retval.append( channels.Analog(i) )
  return retval

def get_digital_channels():
  retval = list()
  for i in [
    'ni/dev1/port0/line0',
    'ni/dev1/port0/line1',
    'ni/dev1/port0/line2',
    'ni/dev1/port0/line3',
    'ni/dev1/port0/line4',
    'ni/dev1/port0/line5',
    'ni/dev1/port0/line6',
    'ni/dev1/port0/line7',
    'ni/dev1/port1/line0',
    'ni/dev1/port1/line1',
    'ni/dev1/port1/line2',
    'ni/dev1/port1/line3',
    'ni/dev1/port1/line4',
    'ni/dev1/port1/line5',
    'ni/dev1/port1/line6',
    'ni/dev1/port1/line7',
    'viewpoint/0/A/0',
    'viewpoint/0/A/1',
    'viewpoint/0/A/2',
    'viewpoint/0/A/3',
    'viewpoint/0/A/4',
    'viewpoint/0/A/5',
    'viewpoint/0/A/6',
    'viewpoint/0/A/7',
  ]: retval.append( channels.Digital(i) )
  return retval

def get_timing_channels():
  retval = list()
  for i in [
    'viewpoint/0/A/0',
    'viewpoint/0/A/1',
    'viewpoint/0/A/2',
    'viewpoint/0/A/3',
    'viewpoint/0/A/4',
    'viewpoint/0/A/5',
    'viewpoint/0/A/6',
    'viewpoint/0/A/7',
  ]: retval.append( channels.Timing(i) )
  return retval

def get_routeable_backplane_signals():
  retval = list()
  for i in [
    'ni/PXI/0',
    'ni/PXI/1',
    'ni/PXI/2',
    'ni/PXI/3',
    'ni/PXI/4',
    'ni/PXI/10MHzClock',
    'ni/dev2/10MHzClock',
    'ni/dev2/20MHzClock',
    'ni/PAF/0',
    'ni/PAF/1',
    'ni/PAF/2',
    'ni/PAF/3',
    'ni/PAF/4',
    'ni/PAF/5',
    'ni/PAF/6',
    'ni/PAF/7',
  ]: retval.append( channels.Backplane(i) )
  return retval

