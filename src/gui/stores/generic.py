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

  def __init__(self, **kwargs):
    gtk.TreeStore.__init__(self,
      str,    # label
      object, # type
      object, # range
      bool,   # bool-value
      str,    # str-value
      int,    # int-value
      float,  # float-value
    )

    TreeModelDispatcher.__init__(self, gtk.TreeStore, **kwargs)


  def dict(self):
    D = dict()
    for i in iter(self):
      if i.parent is not None:
        raise RuntimeError('Parented item at root-level of Generic tree')

      Ddev = D[ i[Generic.LABEL] ] = dict()
      for j in i.iterchildren():
        Ddev[ j[Generic.LABEL] ] = {
          'value'  : j[ Generic.to_index[ j[Generic.TYPE] ] ],
          'type'   : j[Generic.TYPE],
          'range'  : j[Generic.RANGE],
        }

    return D

  def load(self, D):
    self.clear()
    for i in D.items:
      row = list(Generic.default)
      row[0] = i[0]
      parent = self.append( None, row)
      for j in i[1].items():
        row = list(Generic.default)
        row[ Generic.LABEL ]  = j[0]
        row[ Generic.TYPE  ]  = j[1]['type']
        row[ Generic.RANGE ]  = j[1]['range']
        row[ Generic.to_index[ j[1]['type'] ] ] = j[1]['value']
        self.append( parent, row )

  def representation(self):
    return self.dict()
