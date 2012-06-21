# vim: ts=2:sw=2:tw=80:nowrap

from callfunc import CallFunc
import send, compute
from common import *

class StopGeneration(Exception): pass



class Arbwave:
  """
  Class for creating a fake arbwave module to be accessed and used inside
  scripts.
  """
  
  def __init__(self, plotter):
    self.plotter = plotter
    self.devcfg = None
    self.clocks = None
    self.signals = None
    self.channels = None
    self.waveforms = None
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

    analog, digital, transitions, t_max = \
      compute.waveforms( self.devcfg[0],
                         self.clocks[0],
                         self.signals[0],
                         self.channels[0],
                         self.waveforms[0],
                         globals=globals )

    send.to_plotter( self.plotter, analog, digital, self.channels[0], t_max )
    send.to_driver.waveform( analog, digital, transitions, t_max, continuous )
    send.to_driver.start(self.devcfg[0], self.clocks[0], self.signals[0])


  def halt(self):
    send.to_driver.stop()


  def update_static(self, globals=None):
    """
    Only process static outputs and send to plotter.
    """
    exec global_load

    analog, digital = \
      compute.static( self.devcfg[0],
                      self.channels[0],
                      globals=globals )

    send.to_driver.static( analog, digital )


  def update_plotter(self, globals=None):
    """
    Process inputs to send only to plotter.
    """
    exec global_load

    analog, digital, transitions, t_max = \
      compute.waveforms( self.devcfg[0],
                         self.clocks[0],
                         self.signals[0],
                         self.channels[0],
                         self.waveforms[0],
                         globals=globals )

    send.to_plotter( self.plotter, analog, digital, self.channels[0], t_max )


  def request_stop(self, request=True):
    self.stop_requested = request
