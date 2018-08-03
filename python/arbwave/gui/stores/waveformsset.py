# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk
import logging, sys

from .dispatcher import TreeModelDispatcher

from .waveforms import Waveforms

class WaveformsSet(TreeModelDispatcher, gtk.ListStore):
  LABEL     =0
  WAVEFORMS =1

  DEFAULT = 'Default'

  def __init__(self, **kwargs):
    super(WaveformsSet,self).__init__(
      model=gtk.ListStore,
      model_args=(
        str,    # Label
        object, # waveforms
      ),
      # **kwargs
    )
    self.kwargs = kwargs

    self.current_waveform = None
    self._changed_wf_cb = list()
    self._pause_cb = True
    gtk.ListStore.connect(self, 'row-changed', self._row_changed)
    gtk.ListStore.connect(self, 'row-deleted', self._row_deleted)
    self.clear() # set up default
    self._pause_cb = False

  def pause(self):
    self._pause_cb = True
  def unpause(self):
    self._pause_cb = False

  def connect_wf_change(self, cb):
    self._changed_wf_cb.append( cb )

  def disconnect_wf_change(self, cb):
    self._changed_wf_cb.remove( cb )

  def _row_changed(self, treemodel, path, iter):
    if self._pause_cb: return
    #check to see if current label has been changed
    if self.current_waveform not in self.wf_dict():
      # set to next item
      self.set_current( self[iter][WaveformsSet.LABEL] )

  def _row_deleted(self, treemodel, path):
    if self._pause_cb: return
    #check to see if current wf has been deleted.  If all have been deleted,
    #create defaults.
    if len( self ) == 0:
      self.clear(False)
      return
    if self.current_waveform not in self.wf_dict():
      try:
        # set to next item
        self.set_current( self[self.get_iter(path)][WaveformsSet.LABEL] )
      except ValueError:
        self.set_current( self[-1][WaveformsSet.LABEL] )

  def set_current(self, label):
    if label in self.wf_dict():
      self.current_waveform = label
    else:
      raise RuntimeError('Cannot set current waveform to non-existent waveform')
    # tell others now
    if self._pause_cb: return
    for cb in self._changed_wf_cb:
      logging.debug('(cb=%s)( self.current_waveform=%s )...', repr(cb), self.current_waveform )
      cb( self.current_waveform )


  def get_current(self):
    if self.current_waveform not in self.wf_dict():
      raise RuntimeError('Current waveform label is non-existent')
    return self.current_waveform

  def get_current_iter(self):
    for i in iter(self):
      if i[self.LABEL] == self.current_waveform:
        return i.iter
    raise RuntimeError('Current waveform label is non-existent')


  def wf_dict(self):
    D = dict()
    order = 0
    for i in iter(self):
      D[ i[WaveformsSet.LABEL] ] = i[WaveformsSet.WAVEFORMS]
    return D

  def get_wf(self, label=None):
    if label is None:
      label = self.get_current()
    return self.wf_dict()[label]

  def dict(self):
    WFD = dict()
    D = dict( current_waveform=self.get_current(), waveforms=WFD )
    for i in iter(self):
      WFD[ i[WaveformsSet.LABEL] ] = i[WaveformsSet.WAVEFORMS].representation()
    return D

  def get_default(self):
    keys = self.wf_dict().keys()
    for i in range(sys.maxsize):
      ldefault = self.DEFAULT + ( (i != 0 and '_'+str(i)) or '' )
      if ldefault not in keys: break
    return (ldefault, Waveforms( **self.kwargs ))

  def clear(self, doclear=True):
    self.pause()
    if doclear:
      gtk.ListStore.clear(self)
    # create a default waveform
    self.append( self.get_default() )
    self.unpause()
    self.set_current( self.DEFAULT )

  def load(self, D):
    self.pause()
    gtk.ListStore.clear(self)
    for l,wf in D['waveforms'].items():
      WF = Waveforms( **self.kwargs )
      WF.load( wf )

      self.append( (l, WF) )
    self.unpause()
    self.set_current( D['current_waveform'] )

  def representation(self):
    return self.dict()
