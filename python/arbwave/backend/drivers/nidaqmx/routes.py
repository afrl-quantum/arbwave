# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

from ....tools.expand import expand_braces
#import sys
#sys.path.append('../../../tools')
#from expand import expand_braces

class ImplicitRoute(tuple): pass
class NoDevTerminal(str): pass


T5  = 'TRIG/{0..5}'
T6  = 'TRIG/{0..6}'
T7  = 'TRIG/{0..7}'
Ti7 = 'TRIG/7'
R6  = 'RTSI{0..6}'
R7  = 'RTSI{0..7}'
Ri7 = 'RTSI7'
P7  = 'PFI{0..7}'
P9  = 'PFI{0..9}'
P15 = 'PFI{0..15}'
ao_sig = 'ao/{SampleClock,StartTrigger,PauseTrigger,SampleClockTimebase}'
ai_sig = 'ai/{SampleClock,StartTrigger,ReferenceTrigger,ConvertClock,' \
             'PauseTrigger,SampleClockTimebase}'
do_SC = 'do/SampleClock'
di_SC = 'di/SampleClock'
dio_SC = 'd{i,o}/SampleClock'

Ext = ('External/', None)
PXI5= '{PXI_Trig{0..5}}'
PXIi7 = 'PXI_Trig7'
MTB = 'MasterTimebase'
ao_SC = 'ao/SampleClock'
ao_OC = ImplicitRoute( (ao_SC, NoDevTerminal('OnboardClock')) )
ao_ST = 'ao/StartTrigger'
ao_SCTB = 'ao/SampleClockTimebase'
ai_SCTB = 'ai/SampleClockTimebase'
ai_CCTB = 'ai/ConvertClockTimebase'
ai_SC = 'ai/SampleClock'
ai_CC = 'ai/ConvertClock'
ai_ST = 'ai/StartTrigger'
Ctr0  = ImplicitRoute( ('Ctr0', 'Ctr0InternalOutput') )
Ctr1  = ImplicitRoute( ('Ctr1', 'Ctr1InternalOutput') )

available = {
  'pci-6221' : {
    Ext                   : { P15 },
    'PFI{0..5}'           : { (T7,R7), ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}', Ext },
    'PFI{6..15}'          : {          ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}', Ext },
    (T7,R7)               : { P15,     ai_sig, ao_sig, dio_SC, 'Ctr{0,1}{Gate,Source,Aux,ArmStartTrigger,A,B,Z}' },
    ai_SC                 : { P15, (T7,R7), dio_SC },
    ao_SC                 : { ao_SC, P15, (T7,R7),     dio_SC },
       # above allows OnboardClock --> ao_SC
    ai_CC                 : { P15, (T7,R7),            dio_SC },
    ai_ST                 : { P15, (T7,R7), ao_ST, 'Ctr{0,1}{Gate,Aux,ArmStartTrigger}' },
    'ai/ReferenceTrigger' : { P15, (T7,R7),        'Ctr{0,1}{Gate,Aux,ArmStartTrigger}' },
    ao_ST                 : { P15, (T7,R7) },
    dio_SC                : { P15 },
    '20MHzTimebase'       : { ai_CCTB, ai_SCTB, ao_SCTB, 'Ctr{0,1}Source' },
    '80MHzTimebase'       : {                            'Ctr{0,1}Source' },
    '10MHzRefClock'       : { (T7,R7) },
    'ai/PauseTrigger'     : { (T7,R7) },
    'ao/PauseTrigger'     : { (T7,R7) },
    ai_CCTB               : { ai_CC },
    ai_SCTB               : { ai_SC, ai_CCTB },
    'Ctr0Source'          : { P15, (T7,R7), 'Ctr1Gate', 'Ctr1Aux' },
    'Ctr1Source'          : { P15, (T7,R7), 'Ctr0Gate', 'Ctr0Aux' },
    'Ctr0Gate'            : { P15, (T7,R7), 'Ctr1Source', 'Ctr{0,1}Aux' },
    'Ctr1Gate'            : { P15, (T7,R7), 'Ctr0Source', 'Ctr{0,1}Aux' },
    Ctr0                  : { P15, (T7,R7), ai_SC, ai_ST, ao_SC, dio_SC, ai_CC, 'Ctr1Gate', 'Ctr1Aux', 'Ctr1ArmStartTrigger' },
    Ctr1                  : { P15, (T7,R7), ai_SC, ai_ST, ao_SC, dio_SC, ai_CC, 'Ctr0Gate', 'Ctr0Aux', 'Ctr0ArmStartTrigger' },
    'FrequencyOutput'     : { P15, (T7,R7), dio_SC },
    '100kHzTimebase'      : { ai_SCTB, ao_SCTB, 'Ctr{0,1}Source' },
    'ChangeDetectionEvent': { P15, (T7,R7), dio_SC },
    'port0/line{0..7}'    : { Ext },
  },

  'pci-6534' : {
    Ext                   : { P7 },
    'PFI0'                : { (T6,R6), 'Dig0/ReferenceTrigger', Ext },
    'PFI1'                : { (T6,R6), 'Dig1/ReferenceTrigger', Ext },
    'PFI{2,6}'            : { (T6,R6), 'Dig0/{SampleClock,PauseTrigger,StartTrigger}', do_SC, Ext },
    'PFI{3,7}'            : { (T6,R6), 'Dig1/{SampleClock,PauseTrigger,StartTrigger}', do_SC, Ext },
    'PFI4'                : { (T6,R6), 'Dig0/SampleClockTimebase', Ext },
    'PFI5'                : { (T6,R6), 'Dig1/SampleClockTimebase', Ext },
    ('TRIG/0','RTSI/0')   : { P7, ('TRIG/{1..6}', 'RTSI{1..6}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/1','RTSI/1')   : { P7, ('TRIG/{{0..0},{2..6}}', 'RTSI{{0..0},{2..6}}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/2','RTSI/2')   : { P7, ('TRIG/{{0..1},{3..6}}', 'RTSI{{0..1},{3..6}}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/3','RTSI/3')   : { P7, ('TRIG/{{0..2},{4..6}}', 'RTSI{{0..2},{4..6}}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/4','RTSI/4')   : { P7, ('TRIG/{{0..3},{5..6}}', 'RTSI{{0..3},{5..6}}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/5','RTSI/5')   : { P7, ('TRIG/{{0..4},{6..6}}', 'RTSI{{0..4},{6..6}}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/6','RTSI/6')   : { P7, ('TRIG/{0..5}', 'RTSI{0..5}'), do_SC,
                              'Dig{0,1}/{SampleClockTimebase,SampleClock,PauseTigger,StartTrigger,ReferenceTrigger}' },
    ('TRIG/7','RTSI/7')   : {            'Dig{0,1}/SampleClockTimebase', MTB },
    '20MHzTimebase'       : { (Ti7,Ri7), 'Dig{0,1}/SampleClockTimebase', MTB },
    MTB                   : {            'Dig{0,1}/SampleClockTimebase' },
    # These are the real names of the clock devices.  It seems that NIDAQmx only
    # allows us to specify these as clock sources implicitly through the
    # "OnboardClock" name.
    'Dig0/SampleClockTimebase' : { 'PFI4', ('TRIG/{0..6}', 'RTSI{0..6}'), 'Dig0/{SampleClock,PauseTrigger}'},
    'Dig0/SampleClock'    : {                                                          'Dig0/PauseTrigger'},
    'Dig0/ReadyForTransfer':{ 'PFI{2,6}', ('TRIG/{0..6}', 'RTSI{0..6}'), 'Dig0/{SampleClock,PauseTrigger,StartTrigger}'},
    'Dig1/SampleClockTimebase' : { 'PFI5', ('TRIG/{0..6}', 'RTSI{0..6}'), 'Dig1/{SampleClock,PauseTrigger}'},
    'Dig1/SampleClock'    : {                                                          'Dig1/PauseTrigger'},
    'Dig1/ReadyForTransfer':{ 'PFI{3,7}', ('TRIG/{0..6}', 'RTSI{0..6}'), 'Dig1/{SampleClock,PauseTrigger,StartTrigger}'},
    # This is the fake name of the implicit clock(s) used by this digital
    # device.  This just ensures that the OnboardClock can be used properly.
    # Any desired routing from the actual clock used depends on which
    # configuration of ports is used.  According to the 653x user manual
    # (371464d), the actual clock used is given (limited) by:
    #   port/lines used      Timing Group (Dig0 or Dig1)
    # --------------------------------------------------
    #   port 0                  Group 0
    #   port 2                  Group 1
    #   port 0..1               Group 0
    #   port 2..3               Group 1
    #   port 0..3               Group 0
    do_SC                 : { do_SC },
  },

  'pci-6723' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0,1}{Gate,Source}', Ext },
    (T6,R6)               : { ao_sig, 'Ctr{0,1}{Out,Gate,Source}' },
    (Ti7,Ri7)             : {            ao_SCTB, 'Ctr{0,1}Source', MTB },
    ao_SC                 : { ao_SC, 'PFI5', (T6,R6) },
       # above allows OnboardClock --> ao_SC
    ao_ST                 : { 'PFI6', (T6,R6) },
    '20MHzTimebase'       : { (Ti7,Ri7), ao_SCTB, 'Ctr{0,1}Source', MTB },
    'Ctr0Out'             : { (T6,R6) },
    'Ctr0Gate'            : { 'PFI9', (T6,R6) },
    'Ctr0Source'          : { 'PFI8', (T6,R6) },
    Ctr0                  : { (T6,R6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    Ctr1                  : { ao_SC, 'Ctr1Out', 'Ctr0Gate' },
    "{"+MTB+",100kHzTimebase}" : {       ao_SCTB, 'Ctr{0,1}Source' },
  },

  'pci-6733' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0,1}{Gate,Source}', Ext },
    (T6,R6)               : { ao_sig, 'Ctr{0,1}{Out,Gate,Source}', dio_SC },
    (Ti7,Ri7)             : {              ao_SCTB, 'Ctr{0,1}Source', MTB },
    ao_SC                 : { ao_SC, 'PFI5', (T6,R6),              dio_SC },
       # above allows OnboardClock --> ao_SC
    ao_ST                 : { 'PFI6', (T6,R6) },
    '20MHzTimebase'       : { (Ti7,Ri7),   ao_SCTB, 'Ctr{0,1}Source', MTB },
    'Ctr0Out'             : { (T6,R6) },
    'Ctr0Gate'            : { 'PFI9', (T6,R6) },
    'Ctr0Source'          : { 'PFI8', (T6,R6) },
    Ctr0                  : { (T6,R6), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    Ctr1                  : { ao_SC, 'Ctr1Out', 'Ctr0Gate' },
    "{"+MTB+",100kHzTimebase}" : {         ao_SCTB, 'Ctr{0,1}Source' },
  },

  'pxi-6733' : {
    Ext                   : { P9 },
    P9                    : { ao_sig, 'Ctr{0,1}{Gate,Source}', Ext },
    (T5,PXI5)             : { ao_sig, 'Ctr{0,1}{Out,Gate,Source}', dio_SC },
    (Ti7,PXIi7)           : {              ao_SCTB, 'Ctr{0,1}Source', MTB },
    ao_SC                 : { ao_SC, 'PFI5', (T5,PXI5),            dio_SC },
       # above allows OnboardClock --> ao_SC
    ao_ST                 : { 'PFI6', (T5,PXI5) },
    '20MHzTimebase'       : { (Ti7,PXIi7), ao_SCTB, 'Ctr{0,1}Source', MTB },
    'Ctr0Out'             : { (T5,PXI5) },
    'Ctr0Gate'            : { 'PFI9', (T5,PXI5) },
    'Ctr0Source'          : { 'PFI8', (T5,PXI5) },
    Ctr0                  : { (T5,PXI5), 'Ctr0Out', 'Ctr1Gate' },
    'Ctr1Gate'            : { 'PFI4' },
    'Ctr1Source'          : { 'PFI3' },
    Ctr1                  : { ao_SC, 'Ctr1Out', 'Ctr0Gate' },
    "{"+MTB+",100kHzTimebase}" : {         ao_SCTB, 'Ctr{0,1}Source' },
  },
}

available['pxi-6723'] = available['pxi-6733']
available['pci-6225'] = available['pci-6221']
available['pci-6229'] = available['pci-6221'].copy()
available['pci-6229']['port{1..3}/line{0..7}'] = Ext # 32 channels for 6229


def prefix_terminal(prefix, dev, terminal):
  if type(terminal) is NoDevTerminal:
    return terminal
  return '{}/{}/{}'.format(prefix,dev,terminal)

def format_terminals(dev, dest, host_prefix='', prefix=''):
  # for some terminals, we must use a non ni-formatted path to work with
  # the other devices.  An example is 'TRIG/0'.
  # Furthermore, we are required to indicate which terminals can be
  # connected to external cables/busses
  if type(dest) in [ tuple, list ]:
    # we are given both native and recognizable terminal formats
    # this only occurs when we are describing something like TRIG/1 which needs
    # a host prefix, or like External/ which does _not_ need host_prefix
    if dest[1]:
      D  = expand_braces('{}{}'.format(host_prefix, dest[0]))
      ND = expand_braces(prefix_terminal(prefix,dev,dest[1]))
      assert len(D) == len(ND), \
        'NIDAQmx: {} has mismatch terminals to native terminals: {}' \
        .format(dev,repr(dest))
    else:
      D  = expand_braces(dest[0]) # should not need host_prefix
      ND = [None] # must be something like an 'External/' connection
  elif type(dest) is ImplicitRoute:
    # used for implicit routes that exist, for example ctr0 is routed to
    # Ctr0InternalOutput by default
    D  = expand_braces(prefix_terminal(prefix,dev,dest[0]))
    ND = expand_braces(prefix_terminal(prefix,dev,dest[1]))
  else:
    # only native terminal formats
    D = expand_braces('{}/{}/{}'.format(prefix,dev,dest))
    ND = D
  return D, ND

def strip_prefix( s, prefix='' ):
  if s and '/' in s:
    # strip off the 'ni' part but leave the leading '/' since terminals appear
    # to require the leading '/'
    return s[len(prefix):]
  return s

class RouteLoader(object):
  def __init__(self, host_prefix='', prefix=''):
    self.host_prefix = host_prefix
    self.prefix = prefix
    self.available = available

    # map (src, destination) -> (native-src, native-destination)
    self.signal_route_map = dict()
    # map (src) -> [dest0, dest1, ...]
    self.aggregate_map = dict()


  def mk_signal_route_map(self, device, product):
    product = product.lower()
    agg_map = dict()
    route_map = dict()
    for sources in self.available.get(product,[]):
      dest = list()
      ni_dest = list()
      for dest_i in self.available[product][sources]:
        D, ND = format_terminals(device, dest_i, self.host_prefix, self.prefix)
        dest    += D
        ni_dest += ND
      src, ni_src = format_terminals( device, sources,
                                      self.host_prefix, self.prefix )
      for i in xrange( len(src) ):
        agg_map[ src[i] ] = dest
        for j in xrange( len(dest) ):
          route_map[ (src[i], dest[j]) ] = \
            ( strip_prefix(ni_src[i],   self.prefix),
              strip_prefix(ni_dest[j],  self.prefix) )
    return agg_map, route_map

  def __call__(self, device, product):
    agg_map, route_map = self.mk_signal_route_map(device, product)
    self.signal_route_map.update( route_map )
    # for the aggregate map, we'll need to loop through each key to update the
    # target list if the key already has an existing target list.
    for k,v in agg_map.iteritems():
      if k in self.aggregate_map:
        self.aggregate_map[k].extend( v )
      else:
        self.aggregate_map[k] = v
