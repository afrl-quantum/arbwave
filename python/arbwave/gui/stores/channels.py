# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

def scaling_cb( scaling, p, i, channels ):
  # since rows/paths/iters can change, we have to search through and find this
  # scaling before we re-emit the row-changed signal
  for chan in channels:
    if scaling == chan[channels.SCALING]:
      channels.row_changed( chan.path, chan.iter )
      return
  assert False, 'SCALING CB:  THIS CODE SHOULD NEVER BE REACHED!'

def scaling_cb_del( scaling, p, channels ):
  scaling_cb( scaling, p, None, channels )

def check_add_scaling_cb(channels, path, iter):
  chan = channels[iter]
  scaling = chan[channels.SCALING]
  if scaling and scaling not in channels._scaling_callbacks:
    cb_cha = scaling.connect('row-changed', scaling_cb, channels)
    cb_del = scaling.connect('row-deleted', scaling_cb_del, channels)
    channels._scaling_callbacks[scaling] = ( cb_cha, cb_del )

def rm_scaling_cb(channels, path):
  # try to keep the list of callbacks cleaned out
  cb_list = { chan[channels.SCALING]  for chan in channels }
  if None in cb_list:
    cb_list.remove( None ) # in case some channels had not scaling
  for s in set( channels._scaling_callbacks.keys() ) - cb_list:
    channels._scaling_callbacks.pop( s )

class Channels(TreeModelDispatcher, gtk.ListStore):
  LABEL   =0
  DEVICE  =1
  VALUE   =2
  SCALING =3
  UNITS   =4
  ENABLE  =5
  INTERP_ORDER =6
  INTERP_SMOOTHING =7
  OFFSET  =8

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
      str,  # offset in correct units
    )
    self._scaling_callbacks = dict()

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)

    self.connect('row-changed', check_add_scaling_cb)
    self.connect('row-deleted', rm_scaling_cb)


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
        'offset'  : i[Channels.OFFSET],
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
        i[1]['offset'],
      ])

  def representation(self):
    return self.dict()
