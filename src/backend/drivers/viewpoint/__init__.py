# vim: ts=2:sw=2:tw=80:nowrap

import re, logging
from device import Device
import capabilities
from .... import options
from ....path import collect_prefix

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
    devices[str(d)] = d
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


def set_device_config( config, channels ):
  # we need to separate channels first by device
  # (configs are already naturally separated by device)
  # in addition, we use collect_prefix to drop the 'vp/DevX' part of the
  # channel paths
  chans = collect_prefix(channels, 0, 2, 2)
  for d in devices:
    if d in config or d in chans:
      devices[d].set_config( config.get(d,{}), chans.get(d,[]) )


def set_clocks( clocks ):
  clocks = collect_prefix(clocks, 0, 2)
  for d in devices:
    if d in clocks:
      devices[d].set_clocks( clocks[d] )


def set_signals( signals ):
  signals = collect_prefix(signals, 0, 2, tryalso='dest', prefix_list=devices)
  for d in devices:
    devices[d].set_signals( signals.get(d,{}) )


def set_static(analog, digital):
  assert len(analog) == 0, 'Viewpoint does not perform analog output'
  D = dict()
  for di in digital.items():
    m = re.match('([^/]*/Dev[0-9]*)/(.*)', di[0])
    if m.group(1) not in D:
      D[ m.group(1) ] = dict()
    D[ m.group(1) ][ m.group(2) ] = di[1]

  for dev in D.items():
    devices[ dev[0] ].set_output( dev[1] )


def set_waveforms(analog, digital, transitions, t_max, continuous):
  """
  Viewpoint ignores all transition information since it only needs absolute
  timing information.
  """
  assert len(analog) == 0, 'Viewpoint does not perform analog output'
  D = dict()
  for di in digital.items():
    m = re.match('([^/]*/Dev[0-9]*)/(.*)', di[0])
    if m.group(1) not in D:
      D[ m.group(1) ] = dict()
    D[ m.group(1) ][ m.group(2) ] = di[1]

  for dev in D.items():
    # FIXME:  send in clock transitions also
    devices[ dev[0] ].set_waveforms( dev[1], t_max, continuous )


def start_output():
  # FIXME:  clocks will probably need to be started last.  This means, if a
  # particular viewpoint card has a channel being used as a clock, the card will
  # likely have to be started later
  for dev in devices.values():
    dev.start_output()


def stop_output():
  for dev in devices.values():
    dev.stop_output()


def close():
  """Close all devices and uninitialize anything"""
  while devices:
    devname, dev = devices.popitem()
    logging.debug( 'closing viewpoint device: %s', devname )
    del dev
