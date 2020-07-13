# vim: ts=2:sw=2:tw=80:nowrap
"""
Console/cmdline access to Arbwave.

This module provides access to the Arbwave processor, compute engine, and
connections to hardware drivers using a non-gui approach.  This interface is not
ideal to design or develop complicated experimental configurations or related
waveform.  On the other hand, this interface might be ideal to control an
experiment using an Arbwave configuration and waveform in a manner than is
consistent with embedded systems where there is no display.


NOTE:  DO NOT INSTANTIATE THIS CLASS FROM THE GUI.
"""

import numpy as np
import inspect, threading, time
from collections import deque

from .processor import engine
from .processor import for_nogui
from .processor import default
from .processor import executor
from .tools.var_tools import readvars
from .tools.dict import Dict
from . import options
from . import backend

def open_config(filename):
  """Open an arbwave config file.
  
  This function parses executes the python in the given configuration file for
  Arbwave.  The default global environment is established before parsing this
  file (see arbwave.processor.default).

  This function also removes the 'analog', 'digital', 'dds', ... prefix from all
  channels.  These labels are somewhat of a remnant now (I think, though it is
  still possible that the front end uses these to speed some things up), but
  certainly not used/needed/required-not-to-be-there in the backend of Arbwave.
  """
  V = readvars(filename, default.get_globals())

  for C in V['channels'].values():
    C['device'] = C['device'].partition('/')[-1]
  return V

def add_paths_to_waveform(waveform):
  """
  Add path information to the given waveform.  In the gui, path information is
  defined when the waveform is extracted from the UI storage, but only when
  sending to the backend (not when sending to the config file storage).

  Thus, for this non-gui interface for Arbwave, we need the path information to
  be inserted so that errors can be reported appropriately.
  """

  def recurse(W, root):
    for index, I in enumerate(W):
      I['path'] = root + (index,)

      if 'group-label' in I:
        recurse(I['elements'], root + (index,))

  recurse(waveform, tuple())

class CmdLineUI(object):
  """
  A dummy user interface for use on command line/console.
  """

  class UIThread(threading.Thread):
    """Simple thread to simulate GUI thread"""
    def __init__(self):
      super().__init__()
      self.daemon = True # ensure thread exits if program exits
      self.lock = threading.Lock()
      self.queue = deque() # queue of functions to execute
      self.stop_requested = False

    def run(self):
      while not self.stop_requested:
        with self.lock:
          fun_args = None if not self.queue else self.queue.popleft()
        if fun_args:
          fun_args[0](*fun_args[1], **fun_args[2])
        else:
          time.sleep(.1)

    def push(self, fun, *args, **kwargs):
      with self.lock:
        self.queue.append((fun, args, kwargs))


  def __init__(self, engine):
    self.engine = engine
    self.ui_thread = CmdLineUI.UIThread()
    self.ui_thread.start()

  def __del__(self):
    # kill ui thread
    self.ui_thread.stop_requested = True
    self.ui_thread.join(10)
    if self.ui_thread.is_alive():
      raise RuntimeError('Could not halt UI thread')

  def run_in_ui_thread(self, fun, *args, **kwargs):
    self.ui_thread.push(fun, *args, **kwargs)

  class DummyWaveformEditor(object):
    def set_eval_cache(self, *a, **kw):
      pass

  class Plotter(object):
    def start(self, *a, **kw):
      pass
    def plot_analog(self, *a, **kw):
      pass
    def plot_digital(self, *a, **kw):
      pass
    def finish(self, *a, **kw):
      pass

  waveform_editor = DummyWaveformEditor()
  plotter = Plotter()

  def update_runnables(self, *a, **kw):
    pass

  def show_started(self):
    print('started waveform')

  def show_stopped(self):
    print('stopped waveform')

  def get_active_runnable(self):
    return self.engine.get_active_runnable()

  def update_t_max(self, t_max):
    """
    Update the processors expectation of the waveform duration.  This
    information is used to help properly close down runnables and not wait
    beyond the expected duration.
    """
    # this does *not* have to run in the gui thread and is already protected by
    # a thread lock in the processor.
    self.engine.t_max = t_max


class Arbwave(engine.Arbwave, for_nogui.Processor):
  def __init__(self, filename=None, globals = None, **opts):
    """
    Create an arbwave instance using the specified environment as the set of
    global variables.  If globals is None (the default), the global
    environment of the calling function will be used instead.

    When the script for Arbwave is changed, the processor attempts to refresh
    the global environment back to its original state.
    """

    assert Arbwave._instance is None, 'Cannot have more than one Arbwave instance'
    Arbwave._instance = self # update singleton

    if globals is None:
      G = inspect.stack()[1][0].f_globals
    else:
      G = globals

    for k,v in opts.items():
      assert hasattr(options, k), \
        'Optional arguments must match those in arbwave.options'
      setattr(options, k, v)

    ui = CmdLineUI(self)
    self.clear_profiles()
    self._interactive = True
    engine.Arbwave.__init__(self, globals_source=self, ui=ui)
    for_nogui.Processor.__init__(self, ui=ui, globals=G, arbweng=self)

    self.datalog = DataLog()

    self._config_filename = None

    if filename:
      self.open(filename)

  def __del__(self):
    backend.unload_all()
    super().__del__()
    self.ui.__del__()

  def close(self):
    self.__del__()

  @property
  def filename(self):
    return self._config_filename

  def open(self, filename):
    C = open_config(filename)
    self._config_filename = filename
    default.registered_globals['__file__'] = filename
    self.waveform_collection = Dict(C['waveforms'])
    self.runnable_settings = C['runnable_settings']

    self.clear_profiles()
    self._active_runnable = Dict(label='Default', executor='hardware')

    for_nogui.Processor.update(self, (C['hosts'],         True),
                                     (C['devices'],       True),
                                     (C['clocks'],        True),
                                     (C['signals'],       True),
                                     (C['channels'],      True),
                                     #waveforms set already:
                                     (None,               False),
                                     (C['global_script'], True),
                                     toggle_run=False)

  def compile(self, waveform=None, continuous=False):
    if self.active_profile is not None:
      return self.profiles[self.active_profile].outputs

    waveform = self.waveform if waveform is None else waveform
    add_paths_to_waveform(waveform)
    return super().compile(waveform=waveform, continuous=continuous)

  def compile_profile(self, label, continuous=False, *a, **kw):
    self.profiles[label] = Dict(
      inputs=dict(continuous=continuous, **kw),
      outputs=self.compile(continuous=continuous, *a, **kw),
    )

  @property
  def active_profile(self):
    return self._active_profile

  @active_profile.setter
  def active_profile(self, value):
    if value is not None:
      assert value in self.profiles, 'No such profile exists, compile it first'
    self._active_profile = value

  def clear_profiles(self):
    self.profiles = dict()
    self._active_profile = None

  @property
  def active_runnable(self):
    return self._active_runnable.label

  @active_runnable.setter
  def active_runnable(self, value):
    assert value in self.runnables, \
      'No such runnable exists, add it first or select one of ' + \
      ', '.join(self.runnables.keys())
    if value == 'Default':
      self._active_runnable.executor = 'hardware'
    elif self._active_runnable.executor == 'hardware':
      self._active_runnable.executor = 'once'

    self._active_runnable.label = value

  @property
  def executor(self):
    return self._active_runnable.executor

  valid_executors = ['hardware', 'once', 'loop', 'optimize']
  @executor.setter
  def executor(self, value):
    value = value.lower() if value else ''

    assert value in self.valid_executors, \
      'Executor must be one of {}'.format(repr(self.valid_executors))

    if self._active_runnable.label == 'Default':
      assert value =='hardware', 'Default runnable only allows hardware control'
    self._active_runnable.executor = value

  @property
  def interactive(self):
    return self._interactive

  @interactive.setter
  def interactive(self, value):
    self._interactive = bool(value)

  def get_active_runnable(self):
    """
    Return the runnable label and execution control for the runnable that is
    selected as active.  This interface is required Processor.start().
    """
    # test for the simple case of either run-once, or hardware controlled
    if self._active_runnable.label == 'Default' or \
       self._active_runnable.executor == 'once':
      return self._active_runnable.label, None

    exec_label = self._active_runnable.executor
    exec_label = exec_label[0].upper() + exec_label[1:]
    settings_label = '{}:  {}'.format(self._active_runnable.label, exec_label)
    S = self.runnable_settings[settings_label]

    def prep_cancel(*a, **kw):
      def make_cancelled(*a, **kw):
        class Cancelled:
          def onstart(OSelf): pass
          def onstop(OSelf): pass
          def run(OSelf): pass
        return Cancelled()
      return make_cancelled

    # Now we have to build the  more complicated case of either loop or
    # optimize execution control
    if self._active_runnable.executor == 'loop':
      exec_make = executor.loop.Make
      if self.interactive:
        print('About to execute (nested) for loop(s):')
        executor.loop.print_loop(S, self.active_runnable)
        if input('Continue? [Y]/n: ')[:1].lower() not in ['', 'y', 'Y']:
          exec_make = prep_cancel
    elif self._active_runnable.executor == 'optimize':
      exec_make = executor.optimize.Make
      if self.interactive:
        print('About to execute optimizer(s):')
        executor.optimize.print_optimizers(S, self.active_runnable,
                                           self.get_globals())
        if input('Continue? [Y]/n: ')[:1].lower() not in ['', 'y', 'Y']:
          exec_make = prep_cancel
    else:
      raise RuntimeError('Unknown executor: ' + self._active_runnable.executor)

    return self._active_runnable.label, exec_make(S, self.datalog)

  @property
  def waveform_label(self):
    return self.waveform_collection.current_waveform

  @property
  def all_waveform_labels(self):
    return self.waveform_collection.waveforms.keys()

  @waveform_label.setter
  def waveform_label(self, label):
    assert label in self.waveform_collection.waveforms, \
      'Label must represent a waveform in the collection'
    self.waveform_collection.current_waveform = label

  @property
  def waveform(self):
    W = self.waveform_collection.waveforms[self.waveform_label]
    return W

  @waveform.setter
  def waveform(self, value):
    """
    For now, this waveform setter is a silent NO-OP.  Waveforms must already
    exist in the waveform_collection and are selected through the
    'waveform_label' property.
    """
    pass

  def exec_script(self, *a, **kw):
    """
    Simple wrapper over Processor.exec_script to ensure that we do not clear the
    variable that points to this class in the global environment.
    """
    for k in [k for k, v in self.get_globals().items()
              if type(v) == type(self) and v == self]:
      self.clear_globals[k] = self

    super().exec_script(*a, **kw)


class DataLog(object):
  class Table(object):
    def __init__(self, columns, title):
      self.columns = columns
      self.title = title
      self.data = list()
      self.final = False

    def show(self): pass

    def add(self, *data):
      assert len(data) == len(self.columns), 'Data should match column length'
      self.data.append(data)

    @property
    def ndarray(self):
      return np.array(self.data)

    def __repr__(self):
      return 'DataLog.Table(len(cols)={}, N={})' \
             .format(len(self.columns), len(self.data))

  def __init__(self):
    self.tables = list()
    self.keyed = dict()

  def get(self, columns, title=None):
    key = ( columns, title )

    if key in self.keyed:
      old = self.keyed.get(key)
      assert old in self.tables, 'Old data table handle missing'
      if not old.final:
        return old

    new = self.Table(columns, title)
    self.tables.append(new)
    self.keyed[key] = new
    return new
