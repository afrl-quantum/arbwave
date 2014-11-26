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
Ti7 = 'TRIG/7'
R6  = 'RTSI{0..6}'
R7  = 'RTSI{0..7}'
Ri7 = 'RTSI7'
P9  = 'PFI{0..9}'
P15 = 'PFI{0..15}'
ao_sig = 'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}'
ai_sig = 'ai/{SampleClock,StartTrigger,ReferenceTrigger,ConvertClock,' \
             'PauseTrigger,SampleClockTimebase}'
do_SC = 'do/SampleClock'
di_SC = 'di/SampleClock'
dio_SC = 'd{i,o}/SampleClock'
Ext = ('External/', None)
PXI6= '{PXI_Trig{0..5},PXI_Star}'
PXIi7 = 'PXI_Trig7'
MTB = 'MasterTimebase'
ao_SC = 'ao/SampleClock'
ao_ST = 'ao/StartTrigger'
ao_SCTB = 'ao/SampleClockTimebase'
ai_SCTB = 'ai/SampleClockTimebase'
ai_CCTB = 'ai/ConvertClockTimebase'
ai_SC = 'ai/SampleClock'
ai_CC = 'ai/ConvertClock'
ai_ST = 'ai/StartTrigger'

available = {
  'pci-6723' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0,1}{Gate,Source}', Ext },
    (T6,R6)               : { ao_sig, 'Ctr{0,1}{Out,Gate,Source}' },
    (Ti7,Ri7)             : { ao_SCTB,            'Ctr{0,1}Source', MTB },
    ao_SC                 : { 'PFI5', (T6,R6) },
    ao_ST                 : { 'PFI6', (T6,R6) },
    '20MHzTimebase'       : { (Ti7,Ri7), ao_SCTB, 'Ctr{0,1}Source', MTB },
    ao_SCTB               : { ao_SC },
    'Ctr0Out'             : { (T6,R6) },
    'Ctr0Gate'            : { 'PFI9', (T6,R6) },
    'Ctr0Source'          : { 'PFI8', (T6,R6) },
    'Ctr0InternalOutput'  : { (T6,R6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    'Ctr1InternalOutput'  : { ao_SC, 'Ctr1Out', 'Ctr0Gate' },
    "{"+MTB+",100kHzTimebase}" : { ao_SCTB,       'Ctr{0,1}Source' },
  },

  'pxi-6733' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0,1}{Gate,Source}', Ext },
    (T6,PXI6)             : { ao_sig, 'Ctr{0,1}{Out,Gate,Source}', dio_SC },
    (Ti7,PXIi7)           : { ao_SCTB,              'Ctr{0,1}Source', MTB },
    ao_SC                 : { 'PFI5', (T6,PXI6),                   dio_SC },
    ao_ST                 : { 'PFI6', (T6,PXI6) },
    '20MHzTimebase'       : { (Ti7,PXIi7), ao_SCTB, 'Ctr{0,1}Source', MTB },
    ao_SCTB               : { ao_SC },
    'Ctr0Out'             : { (T6,PXI6) },
    'Ctr0Gate'            : { 'PFI9', (T6,PXI6) },
    'Ctr0Source'          : { 'PFI8', (T6,PXI6) },
    'Ctr0InternalOutput'  : { (T6,PXI6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    'Ctr1InternalOutput'  : { ao_SC, 'Ctr1Out', 'Ctr0Gate' },
    "{"+MTB+",100kHzTimebase}" : { ao_SCTB,         'Ctr{0,1}Source' },
  },

  'pci-6221' : {
    Ext                   : { P15 },
    'PFI{0..5}'           : { (T7,R7), ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}', Ext },
    'PFI{6..15}'          : {          ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}', Ext },
    (T7,R7)               : { P15,     ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}' },
    ai_SC                 : { P15, (T7,R7), dio_SC },
    ao_SC                 : { P15, (T7,R7), dio_SC },
    ai_CC                 : { P15, (T7,R7), dio_SC },
    ai_ST                 : { P15, (T7,R7), ao_ST, 'Ctr{0,1}{Gate,Aux,ArmStartTrigger}' },
    'ai/ReferenceTrigger' : { P15, (T7,R7),        'Ctr{0,1}{Gate,Aux,ArmStartTrigger}' },
    ao_ST                 : { P15, (T7,R7) },
    'd{i,o}/StartTrigger' : { P15 },
    '20MHzTimebase'       : { ai_CCTB, ai_SCTB, ao_SCTB, 'Ctr{0,1}Source' },
    '80MHzTimebase'       : {                            'Ctr{0,1}Source' },
    '10MHzRefClock'       : { (T7,R7) },
    'ai/PauseTrigger'     : { (T7,R7) },
    'ao/PauseTrigger'     : { (T7,R7) },
    ai_CCTB               : { ai_CC },
    ai_SCTB               : { ai_SC, ai_CCTB },
    ao_SCTB               : { ao_SC },
    'Ctr0Source'          : { P15, (T7,R7), 'Ctr1Gate', 'Ctr1Aux' },
    'Ctr1Source'          : { P15, (T7,R7), 'Ctr0Gate', 'Ctr0Aux' },
    'Ctr0Gate'            : { P15, (T7,R7), 'Ctr1Source', 'Ctr{0,1}Aux' },
    'Ctr1Gate'            : { P15, (T7,R7), 'Ctr0Source', 'Ctr{0,1}Aux' },
    'Ctr0InternalOutput'  : { P15, (T7,R7), ai_SC, ai_ST, ao_SC, dio_SC, ai_CC, 'Ctr1Gate', 'Ctr1Aux', 'Ctr1ArmStartTrigger' },
    'Ctr1InternalOutput'  : { P15, (T7,R7), ai_SC, ai_ST, ao_SC, dio_SC, ai_CC, 'Ctr0Gate', 'Ctr0Aux', 'Ctr0ArmStartTrigger' },
    'FrequencyOutput'     : { P15, (T7,R7), dio_SC },
    '100kHzTimebase'      : { ai_SCTB, ao_SCTB, 'Ctr{0,1}Source' },
    'ChangeDetectionEvent': { P15, (T7,R7), dio_SC },
  },
}

available['pci-6733'] = available['pci-6723']
available['pxi-6723'] = available['pxi-6733']
available['pci-6229'] = available['pci-6221']


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
