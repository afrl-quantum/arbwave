# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, GObject as gobject

from .dispatcher import TreeModelDispatcher

def ifthen(state, true_val, false_val):
  if state: return true_val
  else:     return false_val

class Generic(TreeModelDispatcher, gtk.TreeStore):
  LABEL     = 0
  TYPE      = 1
  RANGE     = 2
  VAL_BOOL  = 3
  VAL_STR   = 4
  VAL_INT   = 5
  VAL_FLOAT = 6

  to_index = {
    bool : VAL_BOOL,
    str  : VAL_STR,
    int  : VAL_INT,
    float: VAL_FLOAT,
  }

  default = (None, None, None, False, None, 0, 0.0)

  def __init__(self, store_range=False, use_enable=False, keep_order=False, **kwargs):
    super(Generic,self).__init__(
      model=gtk.TreeStore,
      model_args=([ str,    # label
          object, # type
          object, # range
          bool,   # bool-value
          str,    # str-value
          gobject.TYPE_INT64,    # int-value
          float,  # float-value
        ] + ifthen(use_enable,[bool],[])
      ),
      **kwargs
    )
    if use_enable:
      self.ENABLE = 7
      self.default = tuple( list(self.default) + [True] )

    self.use_enable = use_enable
    self.keep_order = keep_order
    self.store_range = store_range


  def _dict_recursive(self, iter, store_range=None):
    if store_range is None:
      store_range = self.store_range
    D = dict()
    order = 0
    for i in iter:
      di = self._dict_recursive(i.iterchildren())
      if di or i[Generic.TYPE ] is None:
        if not di:
          di = dict()

        if self.use_enable or self.keep_order:
          D[ i[Generic.LABEL] ] = Di = dict(parameters=di)
          if self.use_enable:
            Di['enable'] = i[self.ENABLE]
          if self.keep_order:
            Di['order'] = order
        else:
          D[ i[Generic.LABEL] ] = di

      else:
        D[ i[Generic.LABEL] ] = Di = {
          'value'  : i[ Generic.to_index[ i[Generic.TYPE] ] ],
          'type'   : i[ Generic.TYPE ],
        }
        if store_range:
          Di['range'] = i[Generic.RANGE]
        if self.use_enable:
          Di['enable'] = i[self.ENABLE]
        if self.keep_order:
          Di['order'] = order
      order += 1

    return D

  def dict(self, store_range=None):
    return self._dict_recursive( iter(self), store_range )

  def _load_recursive(self, D, parent=None):
    items = D.items()
    if self.keep_order:
      items = sorted(items, key = lambda i : i[1]['order'] )

    for i in items:
      row = list(self.default)
      row[ Generic.LABEL ] = i[0]

      if self.use_enable:
        row[ self.ENABLE ] = i[1]['enable']

      if 'value' in i[1]:
        row[ Generic.TYPE  ]  = i[1]['type']
        if self.store_range:
          row[ Generic.RANGE ]  = i[1]['range']
        row[ Generic.to_index[ i[1]['type'] ] ] = i[1]['value']
        self.append( parent, row )
      else:
        if self.use_enable:
          self._load_recursive(i[1]['parameters'], self.append( parent, row ))
        else:
          self._load_recursive( i[1], self.append( parent, row ) )

  def load(self, D, clear=True):
    if clear:
      self.clear()
    self._load_recursive( D )

  def representation(self, store_range=None):
    return self.dict(store_range)
