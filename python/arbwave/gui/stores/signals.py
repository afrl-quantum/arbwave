# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk

from .dispatcher import TreeModelDispatcher

class Signals(TreeModelDispatcher, gtk.ListStore):
  SOURCE  =0
  DEST    =1
  INVERT  =2

  def __init__(self, **kwargs):
    super(Signals,self).__init__(
      model=gtk.ListStore,
      model_args=(
        str,  # Source
        str,  # Destination
        bool, # invert-polarity
      ),
      **kwargs
    )


  def dict(self):
    D = dict()
    for i in iter(self):
      if not (i[Signals.SOURCE] and i[Signals.DEST]):
        continue # skip rows that are not yet complete
      D[ ( i[Signals.SOURCE], i[Signals.DEST] ) ] = {
        'invert'  : i[Signals.INVERT],
      }
    return D

  def load(self, D):
    self.clear()
    for i in D.items():
      self.append([
        i[0][0], #source
        i[0][1], #destination
        i[1]['invert'],
      ])

  def representation(self):
    return self.dict()
