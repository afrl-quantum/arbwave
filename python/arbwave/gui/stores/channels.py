# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk

from .dispatcher import TreeModelDispatcher

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
  PLOT_SCALE_OFFSET = 9
  PLOT_SCALE_FACTOR = 10

  default_channel=(
    '',   # Label
    '',   # device
    '',   # value
    None, # scaling
    None, # units
    False,# enable
    1,    # interpolation order
    0,    # interpolation smoothing
    None, # output offset
    0.0,  # plot offset
    1.0,  # plot scaling
  )

  def __init__(self, **kwargs):
    super(Channels,self).__init__(
      model=gtk.ListStore,
      model_args=(
        str,  # Label
        str,  # device
        str,  # value
        object, # scaling
        str,  # units
        bool, # enable
        int,  # interpolation order
        float,# interpolation smoothing parameter
        str,  # offset in correct units
        float,# offset for plotting
        float,# scaling factor for plotting
      ),
      **kwargs
    )
    self._scaling_callbacks = dict()

    self.connect('row-changed', check_add_scaling_cb)
    self.connect('row-deleted', rm_scaling_cb)


  def dict(self, strip_dev_type = False):
    """
    See notes in Channels.representation(...).
    """
    if strip_dev_type:
      strip_pfx = lambda x : x.partition('/')[-1] if x else None
    else:
      strip_pfx = lambda x : x

    D = dict()
    order = 0
    for i in iter(self):
      D[ i[Channels.LABEL] ] = {
        'device'  : strip_pfx(i[Channels.DEVICE]),
        'value'   : i[Channels.VALUE],
        'scaling' : [(row[0], row[1]) for row in i[Channels.SCALING]
                      if row[0] or row[1]
                    ] if i[Channels.SCALING] else None, # *or* in case user has half entry
        'units'   : i[Channels.UNITS],
        'enable'  : i[Channels.ENABLE],
        'interp_order' : i[Channels.INTERP_ORDER],
        'interp_smoothing' : i[Channels.INTERP_SMOOTHING],
        'offset'  : i[Channels.OFFSET],
        'plot_scale_offset'  : i[Channels.PLOT_SCALE_OFFSET],
        'plot_scale_factor'  : i[Channels.PLOT_SCALE_FACTOR],
        'order'   : order,
      }

      order += 1
    return D

  def load(self, D):
    self.clear()
    items = sorted(D.items(), key=lambda i: i[1]['order'])
    for i in items:
      slist = None
      if i[1]['scaling']:
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
        i[1]['plot_scale_offset'],
        i[1]['plot_scale_factor'],
      ])

  def representation(self, strip_dev_type = False):
    """
    Give a native python representation of the channels table.
    Options:
      strip_dev_type: Whether 'Digital' and 'Analog' prefixes should be kept in
                      tact or removed. [Default: False]
                      It should be noted that the Arbwave configuration file
                      does not remove these prefixes.  Thus, load(...) should
                      *only* be called using a version that is similar to that
                      generated with strip_dev_type==False.
    """
    return self.dict(strip_dev_type)
