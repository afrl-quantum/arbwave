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

import inspect

from .processor import engine
from .processor import for_nogui
from .processor import default
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

  @staticmethod
  def run_in_ui_thread(fun, *args, **kwargs):
    fun(*args, **kwargs)

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

    ui = CmdLineUI()
    self.clear_profiles()
    engine.Arbwave.__init__(self, globals_source=self, ui=ui)
    for_nogui.Processor.__init__(self, ui=ui, globals=G, arbweng=self)

    self._config_filename = None

    if filename:
      self.open(filename)

  def __del__(self):
    backend.unload_all()
    super().__del__()

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

    self.clear_profiles()

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
