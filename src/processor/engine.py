# vim: ts=2:sw=2:tw=80:nowrap

import inspect
import gtk, gobject
from gui_callbacks import do_gui_operation
import physical

class CallFunc:
  def __init__(self,C,A,K):
    assert callable(C), 'expected callable: ' + repr(C)
    self.C = C
    self.A = A
    self.K = K
  def __call__(self):
    self.C( *self.A, **self.K )

class StopGeneration(Exception): pass

def plot_stuff( plotter, analog, digital ):
  print 'trying to plot stuff...'

def send_to_plotter( plotter, analog, digital ):
  do_gui_operation( plot_stuff, plotter, analog, digital )



global_load = \
"""
if globals is None:
  globals = inspect.stack()[2][0].f_globals
"""


def compute_waveforms( channels, waveforms, signals, globals=None ):
  exec global_load

  analog = None
  digital = None

  t = 0*physical.unit.ms
  for group in waveforms:
    L = dict()
    if group['script']:
      exec group['script'] in globals, L

    L['t'] = t
    t_start = eval( group['time'], globals, L )
    try:    dt,  sub_dt = eval( group['duration'], globals, L )
    except: dt = sub_dt = eval( group['duration'], globals, L )
    L['dt'] = dt
    L['sub_dt'] = sub_dt

    print '(t_start,t_end): ', t_start, t_start + dt

    if not dt:
      # each waveform element _must_ have its own duration
      pass
    else:
      # we use the group dt as the default for waveform elements as well as the
      # group duration that goes into calculating the natural time 't' for the
      # next group
      pass

    if not group['asynchronous']:
      t = t_start + dt

  return analog, digital




class Arbwave:
  """
  Class for creating a fake arbwave module to be accessed and used inside
  scripts.
  """
  
  def __init__(self, plotter):
    self.plotter = plotter
    self.channels = None
    self.waveforms = None
    self.signals = None
    self.start = None
    self.stop = None
    self.loop_control = None
    self.stop_requested = False


  def connect(self, signal, callback, *args, **kwargs):
    if signal == 'start':
      self.start = CallFunc( callback, args, kwargs )
    elif signal == 'stop':
      self.stop = CallFunc( callback, args, kwargs )
    else:
      raise NameError('Unknown signal')


  def set_loop_control( self, callback, *args, **kwargs ):
    self.loop_control = CallFunc( callback, args, kwargs )


  def clear_callbacks(self):
    self.start        = None
    self.stop         = None
    self.loop_control = None


  def update(self, continuous=False, globals=None):
    """
    Process inputs to generate waveform output and send to plotter.
    """
    exec global_load

    if self.stop_requested:
      raise StopGeneration()
    print 'trying to update the hardware to waveform output!!!!'
    if continuous:
      print 'requesting continuous regeneration...'

    analog, digital = \
      compute_waveforms( self.channels[0],
                         self.waveforms[0],
                         self.signals[0],
                         globals=globals )

    send_to_plotter( self.plotter, analog, digital )


  def halt(self):
    print 'sending stop to generation...'


  def update_static(self, globals=None):
    """
    Only process static outputs and send to plotter.
    """
    exec global_load

    print 'trying to update the hardware to static output!!!!'


  def update_plotter(self, globals=None):
    """
    Process inputs to send only to plotter.
    """
    exec global_load

    send_to_plotter( self.plotter, analog=None, digital=None )


  def request_stop(self, request=True):
    self.stop_requested = request
