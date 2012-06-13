# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from ...capabilities import *
import channels

def get_channels(devices, C, *args, **kwargs):
  retval = list()
  for dev in devices.values():
    #nin = dev.config['number-input-ports']
    nin = 0
    for port in [ 'A', 'B', 'C', 'D' ][:(4-nin)]:
      for line in xrange(16):
        retval.append(
          C('{}/{}/{}'.format(dev, port,line), dev=dev, *args, **kwargs)
        )
  return retval

def get_digital_channels(devices):
  return get_channels(devices, channels.Digital)

def get_timing_channels(devices):
  return get_channels(devices, channels.Timing)


routing_bits = {
  ('TRIG/0','A/13','in' ) : 0x1,
  ('A/13','TRIG/0','out') : 0x8,
  ('TRIG/5','A/14','in' ) : 0x2,
  ('A/14','TRIG/5','out') : 0x10,
  ('TRIG/6','A/15','in' ) : 0x4,
  ('A/15','TRIG/6','out') : 0x20,
}

available_routes = {
  # set_attr('port-routing', 0x1) if A/13 is input...
  'TRIG/0' : {
    'destinations' : ['A/13', 'External/'],
    'invertible'   : False,
  }, # TRIG/0 could be either PXI or RTSI
  # set_attr('port-routing', 0x8) if A/13 is output...
  'A/13' : {
    'destinations' : ['TRIG/0', 'External/'],
    'invertible'   : False,
  }, # TRIG/0 could be either PXI or RTSI

  # set_attr('port-routing', 0x2) if A/14 is input
  'TRIG/5' : {
    'destinations' : ['A/14', 'External/'],
    'invertible'   : False,
  }, # TRIG/5 could be either PXI or RTSI
  # set_attr('port-routing', 0x10) if A/14 is output
  'A/14' : {
    'destinations' : ['TRIG/5', 'External/'],
    'invertible'   : False,
  }, # TRIG/5 could be either PXI or RTSI

  # set_attr('port-routing', 0x4) if A/15 is input
  'TRIG/6' : {
    'destinations' : ['A/15', 'External/'],
    'invertible'   : False,
  }, # TRIG/6 could be either PXI or RTSI
  # set_attr('port-routing', 0x20) if A/15 is output
  'A/15' : {
    'destinations' : ['TRIG/6', 'External/'],
    'invertible'   : False,
  }, # TRIG/6 could be either PXI or RTSI

  'External/' : { # usable as a clock, therefore present as routable
    'destinations' : ['PIN20'],
    'invertible'   : False,
  },
}

def get_routeable_backplane_signals(devices):
  retval = get_channels(devices, channels.Backplane,
                        destinations=['External/'], invertible=False )

  # now overwrite the default backplane channels with those with specifics
  for dev in devices:
    for c, r in available_routes.items():
      if c.startswith('A'):
        c = '{d}/{c}'.format(d=dev,c=c)
      rn = list()
      for dest in r['destinations']:
        if dest.startswith('A'):
          rn.append( '{d}/{c}'.format(d=dev,c=dest) )
        else:
          rn.append( dest )
      retval.append( channels.Backplane( c,
                       destinations = rn,
                       invertible   = r['invertible'] ))
  return retval
