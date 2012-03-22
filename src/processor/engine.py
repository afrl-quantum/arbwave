
import gobject

class CallFunc:
  def __init__(self,C,A,K):
    assert callable(C), 'expected callable: ' + repr(C)
    self.C = C
    self.A = A
    self.K = K
  def __call__(self):
    self.C( *self.A, **self.K )

class StopGeneration(Exception): pass

def plot_stuff( data ):
  print 'trying to plot stuff...'

def send_to_plotter( plotter, analog, digital ):
  gobject.idle_add( plot_stuff,
    {'plotter': plotter, 'analog':None, 'digital':None }
  )




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


  def update(self, continuous=False):
    """
    Process inputs to generate waveform output and send to plotter.
    """
    if self.stop_requested:
      raise StopGeneration()
    print 'trying to update the hardware to waveform output!!!!'
    if continuous:
      print 'requesting continuous regeneration...'

    send_to_plotter( self.plotter, analog=None, digital=None )


  def halt(self):
    print 'sending stop to generation...'


  def update_static(self):
    """
    Only process static outputs and send to plotter.
    """
    print 'trying to update the hardware to static output!!!!'


  def update_plotter(self):
    """
    Process inputs to send only to plotter.
    """
    send_to_plotter( self.plotter, analog=None, digital=None )


  def request_stop(self, request=True):
    self.stop_requested = request
