# vim: ts=2:sw=2:tw=80:nowrap
"""
Set of capabilities that each driver may support.
"""

from . import channels

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
  tlist = get_channels(devices, channels.Timing)
  # now add the internal clock(s)
  for dev in devices.values():
    tlist += [
      channels.InternalTiming('{}/Internal_XO'.format(dev), dev=dev),
      channels.InternalTiming('{}/Internal_OCXO'.format(dev), dev=dev),
    ]
  return tlist


def get_routing_bits(host_prefix=''):
  def H(fmt):
    return fmt.format(host_prefix)

  return {
    (H('{}TRIG/1'), 'A/13',        'in' ) : 0x1,
    ('A/13',        H('{}TRIG/1'), 'out') : 0x8,
    (H('{}TRIG/5'), 'A/14',        'in' ) : 0x2,
    ('A/14',        H('{}TRIG/5'), 'out') : 0x10,
    (H('{}TRIG/6'), 'A/15',        'in' ) : 0x4,
    ('A/15',        H('{}TRIG/6'), 'out') : 0x20,
  }

def get_available_routes(host_prefix=''):
  def H(fmt):
    return fmt.format(host_prefix)

  return {
    # set_attr('port-routing', 0x1) if A/13 is input...
    H('{}TRIG/1') : {
      'destinations' : ['A/13', 'External/'],
      'invertible'   : False,
    }, # TRIG/1 could be either PXI or RTSI
    # set_attr('port-routing', 0x8) if A/13 is output...
    'A/13' : {
      'destinations' : [H('{}TRIG/1'), 'External/'],
      'invertible'   : False,
    }, # TRIG/1 could be either PXI or RTSI

    # set_attr('port-routing', 0x2) if A/14 is input
    H('{}TRIG/5') : {
      'destinations' : ['A/14', 'External/'],
      'invertible'   : False,
    }, # TRIG/5 could be either PXI or RTSI
    # set_attr('port-routing', 0x10) if A/14 is output
    'A/14' : {
      'destinations' : [H('{}TRIG/5'), 'External/'],
      'invertible'   : False,
    }, # TRIG/5 could be either PXI or RTSI

    # set_attr('port-routing', 0x4) if A/15 is input
    H('{}TRIG/6') : {
      'destinations' : ['A/15', 'External/'],
      'invertible'   : False,
    }, # TRIG/6 could be either PXI or RTSI
    # set_attr('port-routing', 0x20) if A/15 is output
    'A/15' : {
      'destinations' : [H('{}TRIG/6'), 'External/'],
      'invertible'   : False,
    }, # TRIG/6 could be either PXI or RTSI

    'External/' : { # usable as a clock, therefore present as routable
      'destinations' : ['PIN/20'],
      'invertible'   : False,
    },
  }

def get_routeable_backplane_signals(devices):
  retval = get_channels( devices, channels.Backplane,
                         destinations=['External/'], invertible=False )
  # we turn retval into a dictionary keyed by the src channel so that we can
  # overwrite with the following nested for loops
  retval = { str(i):i for i in retval }

  # now overwrite the default backplane channels with those with specifics
  for dev in devices.values():
    for c, r in get_available_routes(dev.driver.host_prefix).items():
      if c.partition('/')[0] in ['A', 'PIN']:
        c = '{d}/{c}'.format(d=dev,c=c)
      rn = list()
      for dest in r['destinations']:
        if dest.partition('/')[0] in ['A', 'PIN']:
          rn.append( '{d}/{c}'.format(d=dev,c=dest) )
        else:
          rn.append( dest )
      retval[c] = channels.Backplane( c, destinations = rn,
                                      invertible      = r['invertible'] )
  return retval.values()
