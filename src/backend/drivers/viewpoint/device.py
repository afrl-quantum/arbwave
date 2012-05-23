# vim: ts=2:sw=2:tw=80:nowrap

import viewpoint as vp

from ...device import Device as Base
from ....float_range import float_range
import sim
from capabilities import routing_bits


ignored_settings = {
  'out' : ['repetitions',
           'number_transitions',
           'direction',
           'channels',
          ],
  'in'  : ['direction',
           'in', 'channels',
          ]
}


class Device(Base):
  def __init__(self, prefix, board_number, simulated=False):
    Base.__init__(self, name='{}/Dev{}'.format(prefix,board_number))

    Board = vp.Board
    if simulated:
      if board_number > 0:
        raise IndexError('Only one board in simulated mode.')

      Board = sim.Board

    self.board = Board(
      # default to *all* inputs so that all are high-impedance
      vp.Config('in', range(0,64)),
      vp.Config('out', []),
      board=board_number,
    )
    self.clocks_changed = False
    self.clocks = None
    self.signals = None


  def set_config(self, config, channels):
    C = self.board.configs
    old_config = C.copy()
    N = config

    # we have to strip off the device prefix...

    C['out']['channels'] = channels

    for DIR in C:
      for SETTING in C[DIR]:
        if SETTING in ignored_settings[DIR]:
          continue
        C[DIR][SETTING] = N[DIR][SETTING]['value']

    if old_config != C:
      self.board.configure()


  def set_clocks(self, clocks):
    if self.clocks != clocks:
      self.clocks_changed = True
      self.clocks = clocks


  def set_signals(self, signals):
    if self.signals != signals:
      self.signals = signals
      routing = 0x0
      for s in signals.items():
        route = ('/'.join(s[0].split('/')[2:]), s[1]['dest'], 'out')
        if route in routing_bits:
          routing |= routing_bits[route]
      self.board.set_property('port-routes', routing)


  def set_output(self, data):
    self.board.set_output( data )


  def set_waveforms(self, waveforms, t_max, continuous):
    C = self.board.configs
    old_config = C.copy()

    transitions = dict()
    for line in waveforms:
      for g in waveforms[line].values():
        for t in g:
          if t[0] not in transitions:
            transitions[ t[0] ] = dict()
          transitions[ t[0] ][line] = t[1]
    # Add the last "transition" which is really just a final duration
    transitions[ t_max ] = None

    C['out']['repetitions'] = {True:0, False:1}[continuous]
    C['out']['number_transitions'] = len(transitions)

    if old_config != C:
      # we need to reconfigure in some cases
      self.board.configure()

    scans, stat = self.board.out_status()
    if scans.value < len(transitions):
      raise NotImplementedError(
        'FIXME:  what to do when scans < len(transitions)')
    self.board.write(transitions, stat)


  def get_config_template(self):
    T = vp.config.template.copy()
    drop_some_settings( T )
    fix_float_range( T['in'] )
    fix_float_range( T['out'] )
    return T


  def stop_output(self):
    self.board.out_stop()


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
