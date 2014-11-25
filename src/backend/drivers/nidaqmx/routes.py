# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

from ....tools.expand import expand_braces
#import sys
#sys.path.append('../../../tools')
#from expand import expand_braces

# map (src, destination) -> (native-src, native-destination)
signal_route_map = dict()
# map (src) -> [dest0, dest1, ...]
aggregate_map = dict()

T6  = 'TRIG/{0..6}'
T7  = 'TRIG/{0..7}'
R6  = 'RTSI{0..6}'
R7  = 'RTSI{0..7}'
P9  = 'PFI{0..9}'
P15 = 'PFI{0..15}'
ao_sig = 'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}'
ai_sig = 'ai/{SampleClock,StartTrigger,ReferenceTrigger,ConvertClock,' \
             'PauseTrigger,SampleClockTimebase}'
do_sig = 'do/SampleClock'
di_sig = 'di/SampleClock'
Ext = ('External/', None)
PXI6= '{PXI_Trig{0..5},PXI_Star}'

available = {
  'pci-6723' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0..1}{Gate,Source}', Ext },
    (T6,R6)               : { ao_sig, 'Ctr{0..1}{Out,Gate,Source}' },
    ('TRIG/7','RTSI7')    : { 'ao/SampleClockTimebase', 'Ctr{0..1}Source' },
    'Ctr0Out'             : { (T6,R6) },
    'Ctr0Gate'            : { 'PFI9', (T6,R6) },
    'Ctr0Source'          : { 'PFI8', (T6,R6) },
    'Ctr0InternalOutput'  : { (T6,R6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    'Ctr1InternalOutput'  : { 'ao/SampleClock', 'Ctr1Out', 'Ctr0Gate' },
  },

  'pxi-6723' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0..1}{Gate,Source}', Ext },
    (T6,PXI6)             : { ao_sig, 'Ctr{0..1}{Out,Gate,Source}' },
    ('TRIG/7','PXI_Trig7'): { 'ao/SampleClockTimebase', 'Ctr{0..1}Source' },
    'Ctr0Out'             : { (T6,PXI6) },
    'Ctr0Gate'            : { 'PFI9', (T6,PXI6) },
    'Ctr0Source'          : { 'PFI8', (T6,PXI6) },
    'Ctr0InternalOutput'  : { (T6,PXI6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    'Ctr1InternalOutput'  : { 'ao/SampleClock', 'Ctr1Out', 'Ctr0Gate' },
  },

  'pci-6221' : {
    Ext                   : { P15 },
    'PFI{0..5}'           : { R7, ai_sig, ao_sig, di_sig, do_sig,
                             'Ctr{0..1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}',
                              Ext },
    'PFI{6..15}'          : { ai_sig, ao_sig, di_sig, do_sig,
                             'Ctr{0..1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}',
                              Ext },
    (T7,R7)               : { P15, ai_sig, ao_sig, di_sig, do_sig,
                             'Ctr{0..1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}',
                            },
    FIXME
    'Ctr0Out' : { ('TRIG/{0..6}','RTSI{0..6}') },
    'Ctr0Gate' : { 'PFI9', ('TRIG/{0..6}','RTSI{0..6}') },
    'Ctr0Source' : { 'PFI8', ('TRIG/{0..6}','RTSI{0..6}') },
    'Ctr0InternalOutput' : { ('TRIG/{0..6}','RTSI{0..6}'), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate' : { 'PFI4' },
    'Ctr1Source' : { 'PFI3' },
    'Ctr1InternalOutput' : { 'ao/SampleClock', 'Ctr1Out', 'Ctr0Gate' },
  },
}

available['pci-6733'] = available['pci-6723']
available['pxi-6733'] = available['pxi-6723']
available['pci-6229'] = available['pci-6221']
available['pxi-6229'] = available['pxi-6221']


def format_terminals(dev, dest, prefix=''):
  # for some terminals, we must use a non ni-formatted path to work with
  # the other devices.  An example is 'TRIG/0'.
  # Furthermore, we are required to indicate which terminals can be
  # connected to external cables/busses
  if type(dest) in [ tuple, list ]:
    # we are given both native and recognizable terminal formats
    D  = expand_braces(dest[0])
    if dest[1]:
      ND = expand_braces('{}/{}/{}'.format(prefix,dev,dest[1]))
      assert len(D) == len(ND), \
        'NIDAQmx: {} has mismatch terminals to native terminals: {}' \
        .format(dev,repr(dest))
    else:
      ND = [None] # must be something like an 'External/' connection
  else:
    # only native terminal formats
    D = expand_braces('{}/{}/{}'.format(prefix,dev,dest))
    ND = D
  return D, ND

def strip_prefix( s, prefix='' ):
  if s:
    # strip off the 'ni' part but leave the leading '/' since terminals appear
    # to require the leading '/'
    return s[len(prefix):]
  return s

class RouteLoader(object):
  def __init__(self, prefix=''):
    self.prefix = prefix
    self.available = available


  def mk_signal_route_map(self, device, product):
    product = product.lower()
    agg_map = dict()
    route_map = dict()
    for sources in self.available.get(product,[]):
      dest = list()
      ni_dest = list()
      for dest_i in self.available[product][sources]:
        D, ND = format_terminals(device, dest_i, self.prefix)
        dest        += D
        ni_dest += ND
      src, ni_src = format_terminals(device, sources, self.prefix)
      for i in xrange( len(src) ):
        agg_map[ src[i] ] = dest
        for j in xrange( len(dest) ):
          route_map[ (src[i], dest[j]) ] = \
            ( strip_prefix(ni_src[i],   self.prefix),
              strip_prefix(ni_dest[j],  self.prefix) )
    return agg_map, route_map

  def __call__(self, device, product):
    agg_map, route_map = self.mk_signal_route_map(device, product)
    aggregate_map.update( agg_map )
    signal_route_map.update( route_map )
