# vim: ts=2:sw=2:tw=80:nowrap

from copy import deepcopy
from logging import error, warn, debug, log, DEBUG, INFO
import time
import Pyro4
import viewpoint as vp

from physical import unit

from ...device import Device as Base
from ....tools.float_range import float_range
from ....tools.signal_graphs import nearest_terminal
from .capabilities import get_routing_bits


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
  def __init__(self, driver, board_number):
    super(Device,self).__init__(name='{}/Dev{}'.format( driver, board_number ))
    self.driver = driver

    self.board = vp.Board(
      # default to *all* inputs so that all are high-impedance
      vp.Config('in', []), # autoconfigure unused ports as inputs
      vp.Config('out', []),
      board=board_number,
    )
    self.clocks = dict()
    self.signals = dict()
    self.routes = 0x0
    self.t_max = 0.0 * unit.s

    self.possible_clock_sources = { # look at viewpoint library
      '{d}/Internal_XO'.format(d=self)        : vp.CLCK_INTERNAL,
      '{d}/PIN/20'.format(d=self)             : vp.CLCK_EXTERNAL,
      '{H}TRIG/0'.format(H=driver.host_prefix): vp.CLCK_TRIG_0,
      '{d}/Internal_OCXO'.format(d=self)      : vp.CLCK_OCXO,
    }
    self.routing_bits = get_routing_bits(driver.host_prefix)
    self.timing_channels = set()


  def __del__(self):
    self.stop()


  def set_config(self, config, channels, signal_graph):
    debug('vp.Device(%s).set_config(config=%s)', self, config)

    C = self.board.configs
    old_config = deepcopy(C)
    N = config.copy()
    clk = N.pop('clock')['value']

    # we have to strip off the device prefix...

    # ensure that clock channels are added to the output list
    C['out']['channels'] = self.timing_channels.union(channels)
    C['in']['clock'    ] = C['out']['clock'] = \
      self.possible_clock_sources[
        nearest_terminal( clk,
                          set(self.possible_clock_sources.keys()),
                          signal_graph )
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
      self.timing_channels = set()

      pfxlen = len( str(self) )

      C = self.board.configs
      for clk, clkcfg in clocks.items():
        if 'Internal' in clk:
          C['in']['scan_rate'] = \
          C['out']['scan_rate'] = clkcfg['scan_rate']['value']
        else:
          self.timing_channels.add( clk[pfxlen+1:] )



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
        if route in self.routing_bits:
          routing |= self.routing_bits[route]
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
    """
    Set the waveform on the DIO64 device.
      waveforms : see gui/plotter/digital.py for format
      clock_transitions :  dictionary of clocks to dict(ignore,transitions)
      t_max : maximum time of waveforms with units of time
    """
    if set(waveforms.keys()).intersection( clock_transitions.keys() ):
      raise RuntimeError('Viewpoint channels cannot be used as clocks and ' \
                         'digital output simultaneously')

    C = self.board.configs
    old_config = deepcopy(C)

    scan_rate = C['out']['scan_rate']

    transition_map = dict()
    # first add the waveform transitions
    for channel, groups in waveforms.items():
      for wf_path, (encoding, transitions) in groups.items():
        # encoding is currently ignored (i.e. not defined) for digital
        # channel data
        for timestamp, value in transitions:
          transition_map.setdefault(timestamp, {})[channel] = value

    # second, add transtions for channels being used as aperiod clocks
    for channel, cfg in clock_transitions.items():
      if 'Internal' in channel:
        continue

      # as in processor/engine/compute, dt_clk already should be an integer
      # multiple of 1/scan_rate (where multiple is >= 2)
      period = int(round( cfg['dt'] * scan_rate ))
      half_period = period//2
      for t_rise in cfg['transitions']:
        t_rise *= period # rescale t_rise from dt_clk units to 1/scan_rate units
        t_fall = t_rise + half_period
        # we assume that each device using this clock waits for rising edge
        transition_map.setdefault(t_rise, {})[channel] = True
        # finish the clock pulse by lowering it to logic zero
        transition_map.setdefault(t_fall, {})[channel] = False

    t_last = int(round( t_max.coeff * scan_rate ))

    # Add the last "transition" which is really just a final duration
    transition_map[ t_last ] = None

    self.t_max = t_last / scan_rate * unit.s# save for self.wait()

    C['out']['repetitions'] = {True:0, False:1}[continuous]
    # VIEWPOINT FIXME:  They need to fix their bug!
    # This is what it should be if viewpoint fixed it:
    #C['out']['number_transitions'] = len(transition_map)
    if len(transition_map) > 507:
      C['out']['number_transitions'] = 0
      warn('Using VIEWPOINT-bug work around ( number transitions [%d] > 507 )',
           len(transition_map))
    else:
      C['out']['number_transitions'] = len(transition_map)
    #END VIEWPOINT BUG WORKAROUND

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
    if scans.value < len(transition_map):
      raise NotImplementedError(
        'viewpoint scans < len(transition_map); configure failed?')
    self.board.write(transition_map, stat, integer_time=True)
    # we set all the lines being used as clocks to low.  This is done before the
    # waveform is actually started and in preparation of the start signal.
    self.board.set_output(
      { c:False for c in clock_transitions if 'Internal' not in c },
      self.board.out_state )


  @Pyro4.expose
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


  @Pyro4.expose
  def start(self):
    self.board.out_start()


  @Pyro4.expose
  def wait(self):
    if self.board.configs['out']['repetitions'] == 0:
      raise RuntimeError('Cannot wait for continuous waveform to finish')
    debug('dio64: waiting for waveform time to elapse...')
    while True:
      scans, stat = self.board.out_status()
      if (stat.time.value/self.board.configs['out']['scan_rate']) >= self.t_max.coeff:
        debug('dio64: waveform time elapsed.')
        return
      time.sleep(.01) # only need small sleep; allow CPU to switch context


  @Pyro4.expose
  def stop(self):
    try: #allow for a non-initialized board to 'stop'
      b = self.board
    except AttributeError:
      return
    b.out_stop()
    self.t_max = 0.0 * unit.s


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
