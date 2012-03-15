# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

class Channels(TreeModelDispatcher, gtk.ListStore):
  LABEL   =0
  DEVICE  =1
  SCALING =2
  VALUE   =3
  ENABLE  =4

  def __init__(self, **kwargs):
    gtk.ListStore.__init__(self,
      str,  # Label
      str,  # device
      str,  # scaling
      str,  # value
      bool, # enable
    )

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)


  def dict(self):
    D = dict()
    for i in iter(self):
      D[ i[0] ] = {
        'device'  : i[Channels.DEVICE],
        'scaling' : i[Channels.SCALING],
        'value'   : i[Channels.VALUE],
        'enable'  : i[Channels.ENABLE],
      }
    return D

  def load(self, D):
    self.clear()
    for i in D.items():
      self.append([
        i[0],
        i[1]['device'],
        i[1]['scaling'],
        i[1]['value'],
        i[1]['enable'],
      ])

  def representation(self):
    return self.dict()
