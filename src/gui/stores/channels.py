# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

class Channels(TreeModelDispatcher, gtk.ListStore):
  LABEL   =0
  DEVICE  =1
  VALUE   =2
  SCALING =3
  UNITS   =4
  ENABLE  =5
  INTERP_ORDER =6
  INTERP_SMOOTHING =7

  def __init__(self, **kwargs):
    gtk.ListStore.__init__(self,
      str,  # Label
      str,  # device
      str,  # value
      object, # scaling
      str,  # units
      bool, # enable
      int,  # interpolation order
      float,# interpolation smoothing parameter
    )

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)


  def dict(self):
    D = dict()
    order = 0
    for i in iter(self):
      D[ i[Channels.LABEL] ] = {
        'device'  : i[Channels.DEVICE],
        'value'   : i[Channels.VALUE],
        'scaling' : list(),
        'units'   : i[Channels.UNITS],
        'enable'  : i[Channels.ENABLE],
        'interp_order' : i[Channels.INTERP_ORDER],
        'interp_smoothing' : i[Channels.INTERP_SMOOTHING],
        'order'   : order,
      }
      if i[Channels.SCALING]:
        slist = D[ i[Channels.LABEL] ]['scaling']
        for row in i[Channels.SCALING]:
          slist.append( (row[0], row[1]) )

      order += 1
    return D

  def load(self, D):
    self.clear()
    items = D.items()
    items.sort(key=lambda i: i[1]['order'])
    for i in items:
      slist = gtk.ListStore(str,str)
      for row in i[1]['scaling']:
        slist.append( row )

      self.append([
        i[0],
        i[1]['device'],
        i[1]['value'],
        slist,
        i[1]['units'],
        i[1]['enable'],
        i[1]['interp_order'],
        i[1]['interp_smoothing'],
      ])

  def representation(self):
    return self.dict()
