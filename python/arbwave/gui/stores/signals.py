# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

class Signals(TreeModelDispatcher, gtk.ListStore):
  SOURCE  =0
  DEST    =1
  INVERT  =2

  def __init__(self, **kwargs):
    gtk.ListStore.__init__(self,
      str,  # Source
      str,  # Destination
      bool, # invert-polarity
    )

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)


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
