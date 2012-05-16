# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from ...capabilities import *
from ... import channels

def get_channels(devices, C, *args, **kwargs):
  retval = list()
  for dev in devices.values():
    nin = dev.config['number-input-ports']
    for port in [ 'A', 'B', 'C', 'D' ][:(4-nin)]:
      for line in xrange(16):
        retval.append(
          C('{}/{}/{}'.format(dev, port,line), *args, **kwargs)
        )
  return retval

def get_digital_channels(devices):
  return get_channels(devices, channels.Digital)

def get_timing_channels(devices):
  return get_channels(devices, channels.Timing)


available_routes = {
  # set_attr('port-routing', 0x1) if A/13 is input...
  # set_attr('port-routing', 0x8) if A/13 is output...
  'A/13' : {
    'destinations' : ['TRIG/0', 'External/'],
    'invertible'   : False,
  }, # TRIG/0 could be either PXI or RTSI

  # set_attr('port-routing', 0x2) if A/14 is input
  # set_attr('port-routing', 0x10) if A/14 is output
  'A/14' : {
    'destinations' : ['TRIG/5', 'External/'],
    'invertible'   : False,
  }, # TRIG/5 could be either PXI or RTSI

  # set_attr('port-routing', 0x4) if A/15 is input
  # set_attr('port-routing', 0x20) if A/15 is output
  'A/15' : {
    'destinations' : ['TRIG/6', 'External/'],
    'invertible'   : False,
  }, # TRIG/6 could be either PXI or RTSI

  'PIN20' : { # usable as a clock, therefore present as routable
    'destinations' : ['External/'],
    'invertible'   : False,
  },
}

def get_routeable_backplane_signals(devices):
  retval = get_channels(devices, channels.Backplane,
                        destinations=['External/'], invertible=False )

  # now overwrite the default backplane channels with those with specifics
  for dev in devices.values():
    for c, r in available_routes.items():
      retval.append( channels.Backplane( '{}/{}'.format(dev,c),
                       destinations = r['destinations'],
                       invertible   = r['invertible'] ))
  return retval
