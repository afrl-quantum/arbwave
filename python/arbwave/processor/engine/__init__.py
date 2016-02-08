# vim: ts=2:sw=2:tw=80:nowrap

from ...runnable import Runnable

from callfunc import CallFunc
import send, compute

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
      cls._instance = Arbwave(*a, **kw)
    return cls._instance

  # make class variables of these so that users can have them
  BEFORE  = 0x1
  AFTER   = 0x2
  ANYTIME = BEFORE | AFTER

  StopGeneration = StopGeneration
  
  def __init__(self, globals_source, ui):
    """
    Initializes the fake Arbwave module.
    """
    super(Arbwave,self).__init__()
    self._globals_source = globals_source
    self.ui = ui
    self.devcfg = None
    self.clocks = None
    self.signals = None
    self.channels = None
    self.waveforms = None
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

    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         self.waveforms,
                         globals=self._globals_source.get_globals(),
                         continuous=continuous )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, dev_clocks, self.channels, t_max )
    send.to_driver.waveform( analog, digital, transitions, t_max, continuous )
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

    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         self.waveforms,
                         globals=self._globals_source.get_globals() )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_plotter( self.ui.plotter, analog, digital, dev_clocks, self.channels, t_max )


  def save_gnuplot(self, filename=None, fmt=None):
    """
    Process inputs to send to a file in gnuplot type format.
      Arguments:
        filename : either a filehandle of an open file or a name of a file to
                   write to
        fmt      : filename format to use for creating files specific to each
                   clock (if filename is specified and not fmt, then everything
                   is saved in the same file)
                   Example:  file-{}.txt
                    {} will be replaced with the clock name
    """
    assert not (filename is not None == fmt is not None), \
      'must specify either filename or fmt, _not_ both'

    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
      compute.waveforms( self.devcfg,
                         self.clocks,
                         self.signals,
                         self.channels,
                         self.waveforms,
                         globals=self._globals_source.get_globals() )

    self.ui.waveform_editor.set_eval_cache( eval_cache )
    send.to_file( analog, digital, transitions, dev_clocks, self.channels,
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
    return waveform_find( self.waveforms, label, index, ['group-label', 'channel'] )

  def find_group(self, label, index=0):
    """
    Search for group at the current level.
      label : name of group
      index : select the ith occurance of a group label
    """
    return waveform_find( self.waveforms, label, index, ['group-label'] )

  def find_channel(self, label, index=0):
    """
    Search for channel at the current level.
      label : name of channel
      index : select the ith occurance of a channel label
    """
    return waveform_find( self.waveforms, label, index, ['channel'] )


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
