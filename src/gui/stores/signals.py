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
      D[ i[Signals.SOURCE] ] = {
        'dest'    : i[Signals.DEST],
        'invert'  : i[Signals.INVERT],
      }
    return D

  def load(self, D):
    self.clear()
    for i in D.items():
      self.append([
        i[0], #source
        i[1]['dest'],
        i[1]['invert'],
      ])

  def representation(self):
    return self.dict()
