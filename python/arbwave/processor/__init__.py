# vim: ts=2:sw=2:tw=80:nowrap
"""
This package is responsible for the logic that converts waveforms descriptions
to more explicit channel-specific full waveforms.
"""

import sys, threading, traceback, cProfile
from . import engine
from ..tools.gui_callbacks import do_gui_operation
from .. import options
from . import default
from . import messages as msg

class ModuleLike(object):
  def __init__(self, D):
    self.__dict__ = D

class Processor(object):
  def __init__(self, ui):
    super(Processor,self).__init__()
    self.ui = ui
    self.script = ''
    self.Globals = default.get_globals()
    engine.send.to_driver.register_ui(ui)
    self.engine = engine.Arbwave.instance(self,ui)
    self.engine.defaults = ModuleLike( default.registered_globals )
    sys.modules['Arbwave'] = self.engine # fake Arbwave module
    sys.modules['Arbwave.defaults'] = self.engine.defaults
    sys.modules['msg'] = msg
    msg.set_main_window( ui )
    self.running = None
    self.engine_thread = None

    self.lock = threading.Lock()
    self.end_condition = threading.Condition( self.lock )
    self.script_listeners = list()


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
      ( self.engine.waveforms,False ),
      ( self.script,          True, kwargs ),
      toggle_run=False,
    )


  def exec_script(self, script, kwargs=dict()):
    try: self.Globals['__del__'](**kwargs)
    except: pass
    self.engine.clear_runnables()
    self.Globals.clear()
    self.Globals.update( default.get_globals() ) # reset the global environment
    # ensure that the kwargs is not using the original dictionary
    self.Globals['kwargs'] = dict(self.Globals['_kwargs'], **kwargs )
    exec(script, self.Globals)
    self.script = script
    if script:
      self.ui.update_runnables( self.engine.runnables.keys() )
    for l in self.script_listeners:
      l(self.Globals)


  def update(self,hosts,devcfg,clocks,signals,channels,waveforms,script,toggle_run):
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
      self.engine.waveforms = waveforms[0]

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
      if options.pstats:
        profiler = cProfile.Profile()
        profiler.enable()

      do_restart = False
      do_gui_operation( self.ui.show_started )

      self.running = runnable
      try:
        runnable.onstart()
        runnable.run()

      except engine.StopGeneration as e:
        do_restart = e.request & engine.RESTART
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

      if options.pstats:
        profiler.disable()
        options.pstats.add(profiler)


  def start(self): # start a continuous (re)cycling
    run_label, Control = self.ui.get_active_runnable()

    if run_label not in self.engine.runnables:
      print('Runnable ({r}) not found'.format(r=run_label))
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
