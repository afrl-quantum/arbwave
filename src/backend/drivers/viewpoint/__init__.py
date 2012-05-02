# vim: ts=2:sw=2:tw=80:nowrap

from device import Device
import capabilities

def prefix():
  return 'vp'

def name():
  return 'Viewpoint Driver'


# mapping from board index to device
devices = dict()

def load_boards():
  global devices
  boards = list()
  print 'probing for first 10 viewpoint boards...'
  for i in xrange(10):
    try:
      d = Device(i)
    except:
      break
    devices[i] = d
  print 'found {i} viewpoint boards'.format(i=i)


load_boards()

def get_analog_channels():
  return list()

def get_digital_channels():
  return capabilities.get_digital_channels(devices)

def get_timing_channels():
  return capabilities.get_timing_channels(devices)

def get_routeable_backplane_signals():
  return capabilities.get_routeable_backplane_signals(devices)
