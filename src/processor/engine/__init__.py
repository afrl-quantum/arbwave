# vim: ts=2:sw=2:tw=80:nowrap

from callfunc import CallFunc
import send, compute

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
  
  def __init__(self, globals_source, ui):
    self._globals_source = globals_source
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


  def update(self, stop=ANYTIME, continuous=False, wait=True):
    """
    Process inputs to generate waveform output and send to plotter.
    """
    if stop is None:
      stop = 0x0

    if (stop & self.BEFORE) and self.stop_request:
      self.dostop()

    analog, digital, transitions, t_max, end_clocks, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         self.waveforms,
                         globals=self._globals_source.get_globals() )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, self.channels, t_max )
    send.to_driver.waveform( analog, digital, transitions, t_max, end_clocks, continuous )
    send.to_driver.start(self.devcfg, self.clocks, self.signals)
    if wait and not continuous:
      send.to_driver.wait()

    if (stop & self.AFTER) and self.stop_request:
      self.dostop()

  def stop_check(self):
    if self.stop_request:
      self.dostop()


  def halt(self):
    send.to_driver.stop()
    self.update_static()


  def update_static(self):
    """
    Only process static outputs and send to plotter.
    """

    analog, digital = \
      compute.static( self.devcfg,
                      self.channels,
                      globals=self._globals_source.get_globals() )

    send.to_driver.static( analog, digital )


  def update_plotter(self):
    """
    Process inputs to send only to plotter.
    """

    analog, digital, transitions, t_max, end_clocks, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         self.waveforms,
                         globals=self._globals_source.get_globals() )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, self.channels, t_max )


  def request_stop(self, request=STOP, restart=False):
    self.stop_request = request
    if restart:
      self.stop_request |= RESTART
