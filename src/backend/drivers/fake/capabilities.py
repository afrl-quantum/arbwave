# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from ...capabilities import *
import channels

def get_analog_channels():
  retval = list()
  for i in [
    '/dev0/ao0',
    '/dev0/ao1',
    '/dev0/ao2',
    '/dev0/ao3',
  ]: retval.append( channels.Analog(i) )
  return retval

def get_digital_channels():
  retval = list()
  for i in [
    '/dev1/port0/line0',
    '/dev1/port0/line1',
    '/dev1/port0/line2',
    '/dev1/port0/line3',
    '/dev1/port0/line4',
    '/dev1/port0/line5',
    '/dev1/port0/line6',
    '/dev1/port0/line7',
    '/dev1/port1/line0',
    '/dev1/port1/line1',
    '/dev1/port1/line2',
    '/dev1/port1/line3',
    '/dev1/port1/line4',
    '/dev1/port1/line5',
    '/dev1/port1/line6',
    '/dev1/port1/line7',
    '/viewpoint/port0/line0',
    '/viewpoint/port0/line1',
    '/viewpoint/port0/line2',
    '/viewpoint/port0/line3',
    '/viewpoint/port0/line4',
    '/viewpoint/port0/line5',
    '/viewpoint/port0/line6',
    '/viewpoint/port0/line7',
  ]: retval.append( channels.Digital(i) )
  return retval

def get_arbitrary_timing_channels():
  retval = list()
  for i in [
    '/viewpoint/port0/line0',
    '/viewpoint/port0/line1',
    '/viewpoint/port0/line2',
    '/viewpoint/port0/line3',
    '/viewpoint/port0/line4',
    '/viewpoint/port0/line5',
    '/viewpoint/port0/line6',
    '/viewpoint/port0/line7',
  ]: retval.append( channels.Timing(i) )
  return retval

def get_routeable_backplane_signals():
  retval = list()
  for i in [
    '/PXI/0',
    '/PXI/1',
    '/PXI/2',
    '/PXI/3',
    '/PXI/4',
    '10MHzClock',
    '20MHzClock',
    '/PAF/0',
    '/PAF/1',
    '/PAF/2',
    '/PAF/3',
    '/PAF/4',
    '/PAF/5',
    '/PAF/6',
    '/PAF/7',
  ]: retval.append( channels.Backplane(i) )
  return retval

