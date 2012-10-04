# vim: ts=2:sw=2:tw=80:nowrap

from callfunc import CallFunc
import send, compute
from common import *

class StopGeneration(Exception):
  def __init__(self, request, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)
    self.request = request

STOP    = 0x1
RESTART = 0x2

class Arbwave:
  """
  Class for creating a fake arbwave module to be accessed and used inside
  scripts.
  """

  # make class variables of these so that users can have them
  BEFORE  = 0x1
  AFTER   = 0x2
  ANYTIME = BEFORE | AFTER

  StopGeneration = StopGeneration
  
  def __init__(self, ui):
    self.ui = ui
    self.devcfg = None
    self.clocks = None
    self.signals = None
    self.channels = None
    self.waveforms = None
    self.stop_request = False

    class Runnable:
      def extra_data_labels(self):
        """
        Returns list of names of extra results returned by self.run()
        """
        return list()

      def onstart(rself):
        """
        Executed before the runnable is started.
        """
        pass

      def onstop(rself):
        """
        Executed after the runnable is stopped.
        """
        pass

      def run(rself):
        """
        The body of any inner loop.
        """
        self.update(continuous=True)

    self.Runnable = Runnable
    self.runnables = dict( Default = Runnable() )


  def add_runnable( self, label, runnable ):
    """
    Adds a Runnable class to the list of possible runs.
    """
    self.runnables[label] = runnable


  def clear_runnables(self):
    self.runnables = dict( Default = self.Runnable() )


  def dostop(self):
    try: raise StopGeneration( self.stop_request )
    finally: self.stop_request = False


  def update(self, stop=ANYTIME, continuous=False, wait=True, globals=None):
    """
    Process inputs to generate waveform output and send to plotter.
    """
    exec global_load
    if stop is None:
      stop = 0x0

    if (stop & self.BEFORE) and self.stop_request:
      self.dostop()

    analog, digital, transitions, t_max, end_clocks, eval_cache = \
      compute.waveforms( self.devcfg[0],
                         self.clocks[0],
                         self.signals[0],
                         self.channels[0],
                         self.waveforms[0],
                         globals=globals )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, self.channels[0], t_max )
    send.to_driver.waveform( analog, digital, transitions, t_max, end_clocks, continuous )
    send.to_driver.start(self.devcfg[0], self.clocks[0], self.signals[0])
    if wait and not continuous:
      send.to_driver.wait()

    if (stop & self.AFTER) and self.stop_request:
      self.dostop()

  def stop_check(self):
    if self.stop_request:
      self.dostop()


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

    analog, digital, transitions, t_max, end_clocks, eval_cache = \
      compute.waveforms( self.devcfg[0],
                         self.clocks[0],
                         self.signals[0],
                         self.channels[0],
                         self.waveforms[0],
                         globals=globals )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, self.channels[0], t_max )


  def request_stop(self, request=STOP, restart=False):
    self.stop_request = request
    if restart:
      self.stop_request |= RESTART
