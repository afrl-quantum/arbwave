# vim: ts=2:sw=2:tw=80:nowrap

from ...runnable import Runnable
from ...tools.dict import Dict

from .callfunc import CallFunc
from . import send, compute

class StopGeneration(Exception):
  def __init__(self, request, *args, **kwargs):
    Exception.__init__(self, *args, **kwargs)
    self.request = request

STOP    = 0x1
RESTART = 0x2

class Arbwave(object):
  """
  Class for creating a fake Arbwave module to be accessed and used inside
  scripts.
  """

  _instance = None
  @classmethod
  def instance(cls, *a, **kw):
    """
    Singleton access into Arbwave class.
    """
    if cls._instance is None and kw.pop('new',True):
      cls._instance = cls(*a, **kw)
    return cls._instance

  # make class variables of these so that users can have them
  BEFORE  = 0x1
  AFTER   = 0x2
  ANYTIME = BEFORE | AFTER

  StopGeneration = StopGeneration
  STOP = STOP
  RESTART = RESTART
  
  def __init__(self, globals_source, ui):
    """
    Initializes the fake Arbwave module.
    """
    self._globals_source = globals_source
    self.ui = ui
    self.hosts = None
    self.devcfg = None
    self.clocks = None
    self.signals = None
    self.channels = None
    self.waveform = None
    self.stop_request = False

    self.Runnable = Runnable
    self.runnables = dict( Default = Runnable() )


  def add_runnable( self, label, runnable ):
    """
    Adds a Runnable class to the list of possible runs.
    """
    self.runnables[label] = runnable


  def clear_runnables(self):
    self.runnables = dict( Default = Runnable() )


  def dostop(self):
    try: raise StopGeneration( self.stop_request )
    finally: self.stop_request = False


  def compile(self, waveform=None, continuous=False):
    waveform = self.waveform if waveform is None else waveform
    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         waveform,
                         globals=self._globals_source.get_globals(),
                         continuous=continuous )

    return Dict(analog=analog, digital=digital, transitions=transitions,
                dev_clocks=dev_clocks, t_max=t_max, eval_cache=eval_cache)


  def update(self, stop=ANYTIME, continuous=False, wait=True):
    """
    Process inputs to generate waveform output and send to
    plotter.
      <b>stop</b>    [Default : Arbwave.ANYTIME]
        The time at which to test for stop requests during the
        update function.
        Valid values:
          None
            Do not check for stop requests during the update
            function.
          Arbwave.BEFORE
            Before the waveforms are computed and sent to
            hardware.
          Arbwave.AFTER
            After the waveforms are computed and sent to
            hardware.
          Arbwave.ANYTIME
            Either before or after waveforms are computed
            and sent to hardware.
      <b>wait</b>
        Whether to wait until the non-continuous waveform has
        completed before returning from the update function.
    """
    if stop is None:
      stop = 0x0

    if (stop & self.BEFORE) and self.stop_request:
      self.dostop()

    res = self.compile(continuous=continuous)
    self.ui.waveform_editor.set_eval_cache( res.eval_cache )
    send.to_plotter( self.ui, self.ui.plotter, res.analog, res.digital,
                     res.dev_clocks, self.channels, res.t_max )
    send.to_driver.waveform( res.analog, res.digital, res.transitions,
                             res.t_max, continuous )
    send.to_driver.start(self.devcfg, self.clocks, self.signals)
    if wait and not continuous:
      excObjs = send.to_driver.wait()
      if excObjs:
        # notify user of any errors occurred during wait
        send.to_ui_notify( self.ui,
          '<span color="red"><b>Error(s) in waiting for waveforms</b>: \n'
          '  {} \n'
          '</span>\n'.format( '\n  '.join([ repr(e) for e in excObjs ]) )
        )

    if (stop & self.AFTER) and self.stop_request:
      self.dostop()

  def stop_check(self):
    """
    Check to see if a request to stop has been issued and
    stop if so.
    """
    if self.stop_request:
      self.dostop()


  def halt(self):
    """
    Immediately top waveform output and update to static output.
    """
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

    res = self.compile()

    self.ui.waveform_editor.set_eval_cache( res.eval_cache )
    send.to_plotter( self.ui, self.ui.plotter, res.analog, res.digital,
                     res.dev_clocks, self.channels, res.t_max )


  def save_waveform(self, filename, fmt='gnuplot'):
    """
    Save waveform to a file in the specified output format.
      filename : the file to save the waveform to
        If the output file format is for gnuplot, then the filename can be:
          (1) a filehandle of an open file to write to
          (2) a name of a file to open then write to
          (3) or filename format to use for creating files specific to each
              clock.
              Example:  file-{}.txt
               {} will be replaced with the clock name
          If a single filename is specified, everything is saved in the same file

      fmt : either 'gnuplot' or 'python' to specify the output format
    """
    res = self.compile()

    self.ui.waveform_editor.set_eval_cache( res.eval_cache )
    send.to_file( res.analog, res.digital, res.transitions, res.dev_clocks,
                  self.channels,
                  filename, fmt )


  def request_stop(self, request=STOP, restart=False):
    self.stop_request = request
    if restart:
      self.stop_request |= RESTART


  def find(self, label, index=0):
    """
    Search for either channels or groups at the current level.
      label : name of channel or group
      index : select the ith occurance of a channel/group label
    """
    return waveform_find( self.waveform, label, index, ['group-label', 'channel'] )

  def find_group(self, label, index=0):
    """
    Search for group at the current level.
      label : name of group
      index : select the ith occurance of a group label
    """
    return waveform_find( self.waveform, label, index, ['group-label'] )

  def find_channel(self, label, index=0):
    """
    Search for channel at the current level.
      label : name of channel
      index : select the ith occurance of a channel label
    """
    return waveform_find( self.waveform, label, index, ['channel'] )


def waveform_find(elements, label, index, kind):
  i = 0
  for e in elements:
    if True not in [ k in e  for k in kind ]: continue
    if True in [ e[k] == label for k in kind if k in e ]:
      if i == index: return WaveformNode(e)
      i += 1
  raise KeyError('{l}[{i}] not found '.format(l=label,i=index))

class WaveformNode(object):
  def __init__(self, node):
    super(WaveformNode,self).__init__()
    self.node = node

  def __getitem__(self,i):
    return self.node[i]

  def __setitem__(self,i,val):
    self.node[i] = val

  def __repr__(self):
    return repr(self.node)

  def __str__(self):
    return str(self.node)

  def find(self, label, index=0, kind=['group-label','channel']):
    return waveform_find( self['elements'], label, index, kind )

  def find_group(self, label, index=0):
    return waveform_find( self['elements'], label, index, ['group-label'] )

  def find_channel(self, label, index=0):
    return waveform_find( self['elements'], label, index, ['channel'] )
