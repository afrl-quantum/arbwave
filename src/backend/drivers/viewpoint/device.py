# vim: ts=2:sw=2:tw=80:nowrap

from copy import deepcopy
from logging import error, warn, debug, log, DEBUG, INFO
import time
import viewpoint as vp

from ...device import Device as Base
from ....tools.float_range import float_range
from ....tools.signal_graphs import nearest_terminal
from capabilities import routing_bits


ignored_settings = {
  'out' : ['repetitions',
           'number_transitions',
           'direction',
           'channels',
           'clock',
           'scan_rate',
          ],
  'in'  : ['direction',
           'channels',
           'clock',
           'scan_rate',
          ]
}


class Device(Base):
  def __init__(self, prefix, board_number):
    Base.__init__(self, name='{}/Dev{}'.format(prefix,board_number))

    self.board = vp.Board(
      # default to *all* inputs so that all are high-impedance
      vp.Config('in', []), # autoconfigure unused ports as inputs
      vp.Config('out', []),
      board=board_number,
    )
    self.clocks = None
    self.signals = None
    self.routes = 0x0
    self.t_max = 0.0

    self.possible_clock_sources = { # look at viewpoint library
      '{d}/Internal_XO'.format(d=self)    : vp.CLCK_INTERNAL,
      '{d}/PIN/20'.format(d=self)         : vp.CLCK_EXTERNAL,
      'TRIG/0'                            : vp.CLCK_TRIG_0,
      '{d}/Internal_OCXO'.format(d=self)  : vp.CLCK_OCXO,
    }


  def __del__(self):
    self.stop()


  def set_config(self, config, channels, shortest_paths, timing_channels):
    C = self.board.configs
    old_config = deepcopy(C)
    N = config.copy()
    clk = N.pop('clock')['value']

    # we have to strip off the device prefix...

    C['out']['channels'] = channels
    C['in']['clock'    ] = C['out']['clock'] = \
      self.possible_clock_sources[
        nearest_terminal( clk,
                          set(self.possible_clock_sources.keys()),
                          shortest_paths )
      ]
    # we'll not set the scan_rate:
    # If we are using an internal clock, this should have already been set
    # If we are using an external clock, this will be ignored
    #C['in']['scan_rate'] = C['out']['scan_rate'] =

    assert set(N.keys()).issubset(['in', 'out']), \
      'Non-in/out config for Viewpoint?'

    for DIR in N:
      for SETTING in N[DIR]:
        C[DIR][SETTING] = N[DIR][SETTING]['value']

    if old_config != C:
      self.board.configure()


  def set_clocks(self, clocks):
    if self.clocks != clocks:
      self.clocks = clocks

      C = self.board.configs
      for clk in clocks.items():
        if 'Internal' in clk[0]:
          C['in']['scan_rate'] = \
          C['out']['scan_rate'] = clk[1]['scan_rate']['value']


  def set_signals(self, signals):
    if self.signals != signals:
      self.signals = signals
      routing = 0x0
      for src, dst in signals.keys():
        if src.startswith( str(self) ):
          src = '/'.join(src.split('/')[2:])
          #dst = dst
          DIR = 'out'
        else: # just assume 'dest' must be a device channel
          #src = src
          dst = '/'.join(dst.split('/')[2:])
          DIR = 'in'

        route = (src, dst, DIR)
        if route in routing_bits:
          routing |= routing_bits[route]
      self.routes = routing
      self.board.set_property('port-routes', self.routes)


  def set_output(self, data):
    if not self.board.is_configured():
      # because the viewpoint cards need to be configured in order to force
      # output on any channel, we will call configure, just to make sure that
      # this will work.  See the comments in set_waveforms
      self.board.configure()
    self.board.set_output( data )


  def set_waveforms(self, waveforms, clock_transitions, t_max, end_clocks,
                    continuous):
    """
    Set the waveform on the DIO64 device.
      waveforms : see gui/plotter/digital.py for format
      clock_transitions :  dictionary of clocks to transitions
      t_max : maximum time of waveforms
      end_clocks : set of clocks for this device that will need to provide an
        extra clock pulse at t = t_max IN CONTINUOUS MODE ONLY.  This is based
        on the channels that use these clocks.  There are some devices, notably
        National Instruments output hardware, that require an extra clock pulse
        in finite mode so that they can notice that they are finished. 
    """
    if set(waveforms.keys()).intersection( clock_transitions.keys() ):
      raise RuntimeError('Viewpoint channels cannot be used as clocks and ' \
                         'digital output simultaneously')

    C = self.board.configs
    old_config = deepcopy(C)

    scan_clock_period = 1. / C['out']['scan_rate']

    transitions = dict()
    # first add the waveform transitions
    for line in waveforms:
      for g in waveforms[line].values():
        for t in g:
          if t[0] not in transitions:
            transitions[ t[0] ] = dict()
          transitions[ t[0] ][line] = t[1]

    def divider(clock):
      return self.clocks[ '{n}/{c}'.format(n=self,c=clock) ]['divider']['value']

    def mk_half_period(line):
      # the extra .0001 is to ensure we don't have rounding error back to the
      # previous timestep
      return 0.5001 * divider(line) * scan_clock_period

    # second, add transtions for channels being used as aperiod clocks
    for line in clock_transitions:
      if 'Internal' in line:
        continue
      half_period = mk_half_period(line)

      for t_rise in clock_transitions[line]:
        t_fall = t_rise + half_period
        if t_rise not in transitions:
          transitions[ t_rise ] = dict()
        if t_fall not in transitions:
          transitions[ t_fall ] = dict()
        # we assume that each device using this clock waits for rising edge
        transitions[ t_rise ][line] = True
        # finish the clock pulse by lowering it to logic zero
        transitions[ t_fall ][line] = False

    if not continuous:
      t_rise = t_max
      transitions[ t_rise ] = \
        { line:True  for line in end_clocks if 'Internal' not in line }
      for line in end_clocks:
        if 'Internal' in line:  continue

        # make sure that the last pulse for each line is large enough
        t_fall = t_rise + mk_half_period(line)
        t_max  = max( t_max, t_fall + scan_clock_period )
        if t_fall not in transitions:
          transitions[ t_fall ] = dict()
        transitions[ t_fall ][line] = False


    # Add the last "transition" which is really just a final duration
    transitions[ t_max ] = None

    self.t_max = t_max # save for self.wait()

    C['out']['repetitions'] = {True:0, False:1}[continuous]
    C['out']['number_transitions'] = len(transitions)

    debug( 'dio64: out-config: %s', C['out'] )

    # we now _must_ configure, since viewpoint must be configured any time we
    # call self.board.out_stop(), which we _will_ call any time any waveforms
    # need to be changed to ensure synchronization between the various cards
    # if old_config != C:
    #   self.board.configure()
    self.board.configure()

    # we must also reset port routes since configuring seems to clear the
    # internal hardware configuration
    self.board.set_property('port-routes', self.routes)

    scans, stat = self.board.out_status()
    if scans.value < len(transitions):
      raise NotImplementedError(
        'viewpoint scans < len(transitions); configure failed?')
    self.board.write(transitions, stat)
    self.board.set_output(
      { c:False for c in clock_transitions if 'Internal' not in c },
      self.board.out_state )


  def get_config_template(self):
    T = deepcopy(vp.config.template)
    drop_some_settings( T )
    fix_float_range( T['in'] )
    fix_float_range( T['out'] )
    T['clock'] = {
      'value' : '',
      'type'  : str,
      'range' : self.possible_clock_sources.keys(),
    }
    return T


  def start(self):
    self.board.out_start()


  def wait(self):
    if self.board.configs['out']['repetitions'] == 0:
      raise RuntimeError('Cannot wait for continuous waveform to finish')
    debug('dio64: waiting for waveform time to elapse...')
    while True:
      scans, stat = self.board.out_status()
      if (stat.time.value/self.board.configs['out']['scan_rate']) >= self.t_max:
        debug('dio64: waveform time elapsed.')
        return
      time.sleep(.01) # only need small sleep; allow CPU to switch context



  def stop(self):
    try: #allow for a non-initialized board to 'stop'
      b = self.board
    except AttributeError:
      return
    b.out_stop()
    self.t_max = 0.0


def drop_some_settings( T ):
  for DIR in ignored_settings:
    for SETTING in ignored_settings[DIR]:
      try:
        T[DIR].pop(SETTING)
      except KeyError:
        pass

def fix_float_range( T ):
  for i in T:
    D = T[i]
    R = D['range']
    if type(R) is dict:
      D['range'] = float_range( R['min'], R['max'] )
