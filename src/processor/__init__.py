# vim: ts=2:sw=2:tw=80:nowrap
"""
This package is responsible for the logic that converts waveforms descriptions
to more explicit channel-specific full waveforms.
"""

import sys, threading, traceback
import engine
from ..tools.gui_callbacks import do_gui_operation
import default
import messages as msg
from ..tools.path import collect_prefix
from ..tools.signal_graphs import shortest_paths
from ..tools.scaling import calculate as calculate_scaling

def get_range( scaling, globals, **kwargs ):
  """
  Get the minimum and maximum values of a given channels scaling.  Some devices
  can use this to provide more firm limits on channel outputs.  NIDAQmx does
  this, for example.
  """
  if not scaling:
    return None
  # note:  we ignore lines with either empty x _OR_ y values
  vals = calculate_scaling(scaling, globals).keys()
  return dict(min=min(vals), max=max(vals), **kwargs)


class Processor:
  def __init__(self, ui):
    self.ui = ui
    self.Globals = default.get_globals()
    self.engine = engine.Arbwave(self,ui)
    sys.modules['arbwave'] = self.engine # fake arbwave module
    sys.modules['msg'] = msg
    msg.set_main_window( ui )
    self.running = None
    self.engine_thread = None

    self.lock = threading.Lock()
    self.end_condition = threading.Condition( self.lock )


  def __del__(self):
    try: exec '__del__()' in self.Globals
    except: pass


  def get_globals(self):
    return self.Globals


  def exec_script(self, script):
    try: exec '__del__()' in self.Globals
    except: pass
    self.engine.clear_runnables()
    self.Globals = default.get_globals() # reset the global environment
    exec script in self.Globals
    self.ui.update_runnables( self.engine.runnables.keys() )


  def update(self,devcfg,clocks,signals,channels,waveforms,script,toggle_run):
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
        self.exec_script( script[0] )

      # set engine inputs
      self.engine.devcfg    = devcfg[0]
      self.engine.clocks    = clocks[0]
      self.engine.signals   = signals[0]
      self.engine.channels  = channels[0]
      self.engine.waveforms = waveforms[0]

      if clocks[1]:
        engine.send.to_driver.clocks( collect_prefix(clocks[0]) )

      if devcfg[1] or channels[1] or signals[1] or clocks[1]:
        # we need to calculate the shortest connected paths of all signals
        # these paths are used to determine which terminal a device should
        # connect to in order to use a particular clock.
        # Sending config to drivers also depends on clock changes because
        # drivers may need to know (approximate) rates for clocks.  We don't
        # send in clocks[0] since the clocks have already been configured.
        # We'll rely on engine.send.to_driver.config to send in a link to the
        # timing channels.
        sp, graph = shortest_paths( signals[0], *clocks[0] )

        num_node_incidences = [ len(i) for i in graph.node_incidence.values() ]
        if num_node_incidences and max(num_node_incidences) > 1:
          raise RuntimeError('Double driving a terminal/cable is not allowed!')

        engine.send.to_driver.config(
          collect_prefix(devcfg[0]),
          collect_prefix(
            {c['device'] : get_range(c['scaling'],self.Globals,order=c['order'])
              for  c in channels[0].values()
                if c['enable']
            },
            1,
          ),
          sp,
        )

      if signals[1]:
        engine.send.to_driver.signals(collect_prefix(signals[0]))

      if self.running or toggle_run:
        self.start()
      else:
        if channels[1] or script[1]:
          self.engine.update_static()

        # TODO:  have more fine-grained change information:
        #   Instead of just "did channels change" have
        #   1.  channel labels changed
        #   2.  channel calibration changed
        #   3.  channel device(s) changed
        #   4.  channel static value changed
        #   With this information, we would more correctly only update plots or
        #   static output when the corresponding information has changed.
        if channels[1] or script[1] or waveforms[1]:
          self.engine.update_plotter()
    finally:
      self.lock.release()


  def run_loop(self, runnable):
    try:
      do_restart = False
      do_gui_operation( self.ui.show_started )

      self.running = runnable
      try:
        runnable.onstart()
        runnable.run()

      except engine.StopGeneration, e:
        do_restart = e.request & engine.RESTART
      except Exception, e:
        print 'halting waveform output because of unexpected error: ', e
        traceback.print_exc()

      self.engine.halt() # ensure that generation is stopped!

      try:
        runnable.onstop()
      except Exception, e:
        print 'unexpected error in stopping waveform: ', e
        traceback.print_exc()

    finally:
      try:
        self.lock.acquire()
        self.engine_thread = None
        if not do_restart:
          self.running = None
        self.end_condition.notify()
      finally:
        self.lock.release()

      if not do_restart:
        do_gui_operation( self.ui.show_stopped )


  def start(self): # start a continuous (re)cycling
    run_label, Control = self.ui.get_active_runnable()

    if run_label not in self.engine.runnables:
      print 'Runnable ({r}) not found'.format(r=run_label)
      return
    runnable = self.engine.runnables[run_label]

    if run_label != 'Default':
      assert self.engine_thread is None, 'Already existing engine thread?!!'
      if Control:
        runnable = Control( runnable, self.Globals )

      # run the loop control inside its own thread
      self.engine_thread = threading.Thread(
        target=self.run_loop,
        kwargs={ 'runnable' : runnable },
      )
      self.engine_thread.daemon = True # ensure thread exits if program exits
      self.engine_thread.start()

    else:
      # we try to do continuous recycling
      #--> just call show_started()
      #--> don't call show_stopped()
      if not self.running:
        runnable.onstart()
      self.running = runnable
      runnable.run()
      self.ui.show_started()


  def stop(self, toggle_run):
    if self.engine_thread:
      # we get a copy because self.engine_thread will be nulled by thread
      t = self.engine_thread
      self.engine.request_stop(restart=(not toggle_run))
      self.end_condition.wait()
      t.join()
    else:
      self.engine.halt()
      if toggle_run:
        self.running.onstop()
        self.ui.show_stopped()
    if toggle_run:
      self.running = None
