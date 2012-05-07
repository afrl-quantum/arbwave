# vim: ts=2:sw=2:tw=80:nowrap
"""
This package is responsible for the logic that converts waveforms descriptions
to more explicit channel-specific full waveforms.
"""

import sys, threading
import engine
from gui_callbacks import do_gui_operation

class Processor:
  def __init__(self, plotter):
    self.Globals = dict()
    self.engine = engine.Arbwave(plotter)
    sys.modules['arbwave'] = self.engine # fake arbwave module
    self.running = False
    self.engine_thread = None

    self.lock = threading.Lock()
    self.end_condition = threading.Condition( self.lock )


  def get_globals(self):
    return self.Globals


  def update(self, channels, waveforms, signals, script, toggle_run, show_stopped):
    """
    Updates that are driven from user-interface changes sent to the engine.
    """
    try:
      self.lock.acquire()

      if self.running:
        self.stop(toggle_run) # might be a race condition
        toggle_run = False

      # First:  update the global script environment
      if script[1]:
        self.engine.clear_callbacks()
        exec script[0] in self.Globals

      # set engine inputs
      self.engine.channels  = channels
      self.engine.waveforms = waveforms
      self.engine.signals   = signals

      if self.running or toggle_run:
        self.start( show_stopped )
      else:
        if channels[1] or script[1] or signals[1]:
          exec 'import arbwave\narbwave.update_static()' in self.Globals

        # TODO:  have more fine-grained change information:
        #   Instead of just "did channels change" have
        #   1.  channel labels changed
        #   2.  channel calibration changed
        #   3.  channel device(s) changed
        #   4.  channel static value changed
        #   With this information, we would more correctly only update plots or
        #   static output when the corresponding information has changed.
        if channels[1] or script[1] or signals[1] or waveforms[1]:
          exec 'import arbwave\narbwave.update_plotter()' in self.Globals
    finally:
      self.lock.release()


  def run_loop(self, show_stopped):
    assert callable(show_stopped), 'expected callable show_stopped'
    if self.engine.start:
      exec 'import arbwave\narbwave.start()' in self.Globals

    try:
      exec 'import arbwave\narbwave.loop_control()' in self.Globals
    except engine.StopGeneration: pass

    self.engine.halt() # ensure that generation is stopped!

    if self.engine.stop:
      exec 'import arbwave\narbwave.stop()' in self.Globals

    try:
      self.lock.acquire()
      self.running = False
      self.engine_thread = None
      do_gui_operation( show_stopped )
      self.end_condition.notify()
    finally:
      self.lock.release()


  def start(self, show_stopped): # start a continuous (re)cycling
    self.engine.request_stop(False)

    if self.engine.loop_control:
      assert self.engine_thread is None, 'Already existing engine thread?!!'

      # run the loop control inside its own thread
      self.engine_thread = threading.Thread(
        target=self.run_loop,
        kwargs={ 'show_stopped' : show_stopped },
      )
      self.engine_thread.daemon = True # ensure thread exits if program exits
      self.engine_thread.start()

    else: # we try to do continuous recycling--> don't call show_stopped()
      if not self.running and self.engine.start:
        exec 'import arbwave\narbwave.start()' in self.Globals
      exec 'import arbwave\narbwave.update(continuous=True)' in self.Globals
    self.running = True


  def stop(self, toggle_run):
    if self.engine_thread:
      # we get a copy because self.engine_thread will be nulled by thread
      t = self.engine_thread
      self.engine.request_stop()
      self.end_condition.wait()
      t.join()
    elif toggle_run:
      self.engine.halt()
      if self.engine.stop:
        exec 'import arbwave\narbwave.stop()' in self.Globals
    if toggle_run:
      self.running = False
