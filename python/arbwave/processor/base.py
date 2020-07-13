# vim: ts=2:sw=2:tw=80:nowrap
"""
Base implementation of the processor class.
"""

import sys, threading, traceback, cProfile, time
from . import engine
from .. import options
from ..tools.dict import Dict
from . import default

class ModuleLike(object):
  def __init__(self, D):
    self.__dict__ = D

class Processor(object):
  def __init__(self, ui, globals=dict(), arbweng=None):
    self.ui = ui
    self.script = ''
    self.Globals = globals
    self.clear_globals = self.Globals.copy() # backup of original globals
    self.Globals.update( default.get_globals() )
    engine.send.to_driver.register_ui(self.ui)
    if arbweng is None:
      self.engine = engine.Arbwave.instance(self, self.ui)
    else:
      self.engine = arbweng
    self.engine.defaults = ModuleLike( default.registered_globals )
    sys.modules['Arbwave'] = self.engine # fake Arbwave module
    sys.modules['Arbwave.defaults'] = self.engine.defaults
    self.running = Dict(runnable=None, thread=None)

    self.lock = threading.Lock()
    self._t_max = None # last known waveform duration (helps waiting for stop)
    self.script_listeners = list()

    super().__init__()


  def __del__(self):
    try: exec('__del__()', self.Globals)
    except: pass

  def connect_listener(self, functor):
    self.script_listeners.append( functor )


  def get_globals(self):
    return self.Globals


  def reset(self, **kwargs):
    """
    Run the same script again.
    """
    self.update(
      ( self.engine.hosts,    False ),
      ( self.engine.devcfg,   False ),
      ( self.engine.clocks,   False ),
      ( self.engine.signals,  False ),
      ( self.engine.channels, False ),
      ( self.engine.waveform, False ),
      ( self.script,          True, kwargs ),
      toggle_run=False,
    )


  def exec_script(self, script, kwargs=dict()):
    try: self.Globals['__del__'](**kwargs)
    except: pass
    self.engine.clear_runnables()
    self.Globals.clear()
    self.Globals.update( self.clear_globals ) # reset the global environment
    self.Globals.update( default.get_globals() ) # add all registered globals
    # ensure that the kwargs is not using the original dictionary
    self.Globals['kwargs'] = dict(self.Globals['_kwargs'], **kwargs )
    code = compile(script, 'global_script', 'exec')
    exec(code, self.Globals)
    self.script = script
    if script:
      self.ui.update_runnables( self.engine.runnables.keys() )
    for l in self.script_listeners:
      l(self.Globals)


  def update(self,hosts,devcfg,clocks,signals,channels,waveforms,script,toggle_run):
    """
    Updates that are driven from user-interface changes sent to the engine.
    """

    needs_start = False
    if not self.stopped:
      needs_start = not toggle_run
      self.stop(toggle_run=toggle_run)
    else:
      needs_start = toggle_run

    # First:  update the global script environment
    if script[1]:
      kw = dict()
      if len(script) == 3:
        kw = script[2]
      self.exec_script( script[0], kwargs=kw )

    # set engine inputs
    self.engine.hosts     = hosts[0]
    self.engine.devcfg    = devcfg[0]
    self.engine.clocks    = clocks[0]
    self.engine.signals   = signals[0]
    self.engine.channels  = channels[0]
    self.engine.waveform  = waveforms[0]

    # the very first bit of real work should be to re-init all connections
    if hosts[1]:
      if engine.send.to_driver.hosts( hosts[0] ):
        # there was a fundamental change in connections.  We will try to send
        # all pieces of the puzzle now.
        devcfg     = ( devcfg[0]   , True )
        clocks     = ( clocks[0]   , True )
        signals    = ( signals[0]  , True )
        channels   = ( channels[0] , True )
        waveforms  = ( waveforms[0], True )

    if clocks[1]:
      engine.send.to_driver.clocks( clocks[0] )

    if devcfg[1] or channels[1] or signals[1] or clocks[1]:
      engine.send.to_driver.config( devcfg[0], channels[0],
                                    signals[0], clocks[0], self.Globals )

    if signals[1]:
      engine.send.to_driver.signals( signals[0] )

    if needs_start:
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


  def run_loop(self, runnable):
    try:
      if options.pstats:
        profiler = cProfile.Profile()
        profiler.enable()

      do_restart = False
      stop_requested = False
      self.ui.run_in_ui_thread( self.ui.show_started )

      try:
        runnable.onstart()
        runnable.run()

      except engine.StopGeneration as e:
        do_restart = e.request & engine.RESTART
        stop_requested = e.request & engine.STOP
      except Exception as e:
        print('halting waveform output because of unexpected error: ', e)
        traceback.print_exc()

      self.engine.halt() # ensure that generation is stopped!

      try:
        runnable.onstop()
      except Exception as e:
        print('unexpected error in stopping waveform: ', e)
        traceback.print_exc()

    finally:
      if options.pstats:
        profiler.disable()
        options.pstats.add(profiler)

      # let main thread collect resources and mark toggle button as stopped
      # only explicitly call for stop from this end if a stop was not already
      # requested.  If requested, we expect the requester calls the clean up
      # code directly.
      if not stop_requested:
        self.ui.run_in_ui_thread(self.stop, toggle_run=not do_restart)


  def start(self): # start a continuous (re)cycling
    run_label, Control = self.ui.get_active_runnable()

    if run_label not in self.engine.runnables:
      print('Runnable ({r}) not found'.format(r=run_label))
      return

    assert self.stopped, 'Already running!!!'

    self.running.runnable = self.engine.runnables[run_label]
    if run_label != 'Default':
      if Control:
        # wrap runnable in the control loop
        self.running.runnable = Control( self.running.runnable, self.Globals )

      # run the loop control inside its own thread
      self.running.thread = threading.Thread(
        target=self.run_loop,
        kwargs={ 'runnable' : self.running.runnable },
      )
      self.running.thread.daemon = True # ensure thread exits if program exits
      self.running.thread.start()

    else: # the Default runnable (only for hardware driven repeats)
      # we try to do continuous recycling
      #--> just call show_started()
      #--> don't call show_stopped()
      self.running.thread = self
      self.running.runnable.onstart()
      self.running.runnable.run()
      self.ui.show_started()


  @property
  def stopped(self):
    if self.running.runnable is not None:
      if self.running.thread is None:
        raise RuntimeError('Missing thread for runnable')

      # 'Default' hardware-run runnable or thread is still running
      if self.running.thread == self or self.running.thread.is_alive():
        return False

      self.running.thread.join()
      return True

    if self.running.thread is not None:
      if self.running.thread.is_alive():
        raise RuntimeError('Child thread running for unknown runnable')
      self.running.thread.join()

    return True


  def stop(self, timeout=None, toggle_run=True):
    """
    Instruct the executing thread to stop.  The requested timeout will limit how
    much time we wait for it to finish.  If no requested timeout is given, 110%
    of the last known waveform duration will be used.  If there is no last known
    duration, 10s will be used.
    """
    if self.stopped:
      if toggle_run:
        self.ui.show_stopped()
      return

    if self.running.thread == self:
      # stopping the hardware-timed, continuous 'Default' runnable
      self.engine.halt()
      if toggle_run:
        self.running.runnable.onstop()
    else:
      # stopping a thread-run runnable
      if not self.stopped:
        self.engine.request_stop(restart=(not toggle_run))

      if timeout is None:
        # The extra 1*s is to allow for overhead of thread management
        t_max = self.t_max
        timeout = 10 if t_max is None else 1 + float(1.1*t_max)

      t0 = time.time()
      self.running.thread.join(timeout=timeout)
      t1 = time.time()
      if not self.stopped:
        raise RuntimeError(
          'Failed waiting {}s (up to {}s) for executing thread to stop'
          .format(t1-t0, timeout))

    self.running.runnable = None
    self.running.thread = None

    if toggle_run:
      self.ui.show_stopped()

  @property
  def t_max(self):
    with self.lock:
      return self._t_max

  @t_max.setter
  def t_max(self, value):
    with self.lock:
      self._t_max = value
