# vim: ts=2:sw=2:tw=80:nowrap

from copy import deepcopy
import viewpoint as vp

from ...device import Device as Base
from ....float_range import float_range
from ....signal_graphs import nearest_terminal
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
    self.clocks_changed = False
    self.clocks = None
    self.signals = None
    self.routes = 0x0

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
      self.clocks_changed = True
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


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
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

    # second, add transtions for channels being used as aperiod clocks
    for line in clock_transitions:
      if 'Internal' in line:
        continue
      for t_rising in clock_transitions[line]:
        t_falling = t_rising + scan_clock_period
        if t_rising not in transitions:
          transitions[ t_rising ] = dict()
        if t_falling not in transitions:
          transitions[ t_falling ] = dict()
        # we assume that each device using this clock waits for rising edge
        transitions[ t_rising ][line] = True
        # finish the clock pulse by lowering it to logic zero
        transitions[ t_falling ][line] = False
    # Add the last "transition" which is really just a final duration
    transitions[ t_max ] = None

    C['out']['repetitions'] = {True:0, False:1}[continuous]
    C['out']['number_transitions'] = len(transitions)

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


  def stop(self):
    try: #allow for a non-initialized board to 'stop'
      b = self.board
    except AttributeError:
      return
    b.out_stop()


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
