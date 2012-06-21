# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

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

  def __init__(self, store_range=False, **kwargs):
    gtk.TreeStore.__init__(self,
      str,    # label
      object, # type
      object, # range
      bool,   # bool-value
      str,    # str-value
      int,    # int-value
      float,  # float-value
    )
    self.store_range = store_range

    TreeModelDispatcher.__init__(self, gtk.TreeStore, **kwargs)


  def _dict_recursive(self, iter, store_range=None):
    if store_range is None:
      store_range = self.store_range
    D = dict()
    for i in iter:
      di = self._dict_recursive(i.iterchildren())
      if di:
        D[ i[Generic.LABEL] ] = di
      elif i[ Generic.TYPE ] is None:
        D[ i[Generic.LABEL] ] = dict()
      else:
        D[ i[Generic.LABEL] ] = Di = {
          'value'  : i[ Generic.to_index[ i[Generic.TYPE] ] ],
          'type'   : i[Generic.TYPE],
        }
        if store_range:
          Di['range'] = i[Generic.RANGE]

    return D

  def dict(self, store_range=None):
    return self._dict_recursive( iter(self), store_range )

  def _load_recursive(self, D, parent=None):
    for i in D.items():
      row = list(Generic.default)
      row[ Generic.LABEL ] = i[0]

      if 'value' in i[1]:
        row[ Generic.TYPE  ]  = i[1]['type']
        if self.store_range:
          row[ Generic.RANGE ]  = i[1]['range']
        row[ Generic.to_index[ i[1]['type'] ] ] = i[1]['value']
        self.append( parent, row )
      else:
        self._load_recursive( i[1], self.append( parent, row ) )

  def load(self, D, clear=True):
    if clear:
      self.clear()
    self._load_recursive( D )

  def representation(self, store_range=None):
    return self.dict(store_range)

if __name__ == '__main__':
  print 'testing loading with empty config-tree:'
  data0 = { 'clock' : { }, }

  g = Generic()
  g.load( data0 )
  print '... no complaints so far'

  print 'testing representation:'
  data_out = g.representation()
  if data0 == data_out:
    print 'success!'
  else:
    print 'input does not equal output'


  print ''
  print 'testing loading with more complicated config-tree:'
  data0 = {
    'Dev1' : {
      'out' : {
        'param0' : { 'type': int, 'range':xrange(10), 'value': 2 },
        'param1' : { 'type': str, 'range':['a','b'], 'value': 'b' },
      },
      'in' : {
        'param2' : { 'type': bool, 'range':None, 'value': False },
        'param3' : { 'type': float, 'range':xrange(-10,30), 'value': 0.3 },
      },
    },
  }

  g = Generic(store_range=True)
  g.load( data0 )
  print '... no complaints so far'

  print 'testing representation:'
  data_out = g.representation()
  if data0 == data_out:
    print 'success!'
  else:
    print 'input does not equal output'
