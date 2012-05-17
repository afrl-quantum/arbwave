# vim: ts=2:sw=2:tw=80:nowrap

import re
from device import Device
import capabilities
from .... import options

def prefix():
  return 'vp'


def name():
  return 'Viewpoint Driver'


def is_simulated():
  return options.simulated


# mapping from board index to device
devices = dict()

def load_boards():
  global devices
  print 'probing for first 10 viewpoint boards...'
  for i in xrange(10):
    try:
      d = Device( prefix(), i, simulated=options.simulated )
    except:
      break
    devices[i] = d
  print 'found {i} viewpoint boards'.format(i=i)


load_boards()

def get_devices():
  return devices.values()

def get_analog_channels():
  return list()

def get_digital_channels():
  return capabilities.get_digital_channels(devices)

def get_timing_channels():
  return capabilities.get_timing_channels(devices)

def get_routeable_backplane_signals():
  return capabilities.get_routeable_backplane_signals(devices)

def set_static(analog, digital):
  assert len(analog) == 0, 'Viewpoint does not perform analog output'
  D = dict()
  for di in digital.items():
    m = re.match('[^/]*/Dev([0-9]*)/(.*)', di[0])
    if m.group(1) not in D:
      D[ m.group(1) ] = dict()
    D[ m.group(1) ][ m.group(2) ] = di[1]

  for dev in D.items():
    devices[int(dev[0])].set_output( dev[1] )
