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


  def list(self):
    L = list()
    for i in iter(self):
      L.append({
        'source'  : i[Signals.SOURCE],
        'dest'    : i[Signals.DEST],
        'invert'  : i[Signals.INVERT],
      })
    return L

  def load(self, L):
    self.clear()
    for i in L:
      self.append([
        i['source'],
        i['dest'],
        i['invert'],
      ])

  def representation(self):
    return self.list()
