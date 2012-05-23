# vim: ts=2:sw=2:tw=80:nowrap

import gtk
import spreadsheet
import helpers

def coerce_range( editable, TYPE ):
  v = TYPE(editable.get_text())
  r = editable.get_range()
  if v < r[0]:
    editable.set_text( str(TYPE(r[0])) )
  elif v > r[1]:
    editable.set_text( str(TYPE(r[1])) )

def set_range( cell, editable, path, model ):
  row = model[path]
  adj = editable.get_adjustment()
  mn = min(row[model.RANGE])
  mx = max(row[model.RANGE])
  TYPE = row[model.TYPE]

  editable.connect('activate', coerce_range, TYPE )

  if TYPE is int:
    adj.configure(row[model.VAL_INT], mn, mx, 1, max(1,.1*(mx-mn)), 0)
  elif TYPE is float:
    adj.configure(row[model.VAL_FLOAT], mn, mx, .01*(mx-mn), .1*(mx-mn), 0)
  else:
    raise RuntimeError('expected int or float')


def load_combobox( cell, editable, path, model ):
  L = gtk.ListStore( str, str )
  editable.set_model( L )
  RANGE = model[path][model.RANGE]
  if callable(RANGE):
    RANGE = RANGE()

  for i in RANGE:
    if type(i) in [list,tuple]:
      L.append( (str(i[0]), '{}: {}'.format(i[0],i[1])) )
    else:
      L.append( (str(i), str(i)) )

  # set up to combo to display the label not the value
  editable.clear()
  renderer = gtk.CellRendererText()
  editable.pack_start( renderer )
  editable.add_attribute( renderer, 'text', 1 )



class Generic:
  def __init__(self, model, add_undo=None):
    self.add_undo = add_undo

    V = self.view = gtk.TreeView(model)
    V.set_property( 'rules-hint', True )
    sheet_cb = spreadsheet.Callbacks(V)

    R = {
      'label'     : gtk.CellRendererText(),
      'val:bool'  : gtk.CellRendererToggle(),
      'val:text'  : gtk.CellRendererText(),
      'val:int'   : gtk.CellRendererSpin(),
      'val:float' : gtk.CellRendererSpin(),
      'cmb:text'  : gtk.CellRendererCombo(),
      'cmb:int'   : gtk.CellRendererCombo(),
      'cmb:float' : gtk.CellRendererCombo(),
    }
    R['val:bool' ].set_property( 'activatable', True )
    R['val:text' ].set_property( 'editable', True )
    R['val:int'  ].set_property( 'editable', True )
    R['val:float'].set_property( 'editable', True )
    R['cmb:text' ].set_property( 'editable', True )
    R['cmb:int'  ].set_property( 'editable', True )
    R['cmb:float'].set_property( 'editable', True )

    R['cmb:text' ].set_property( 'text-column', 0 )
    R['cmb:int'  ].set_property( 'text-column', 0 )
    R['cmb:float'].set_property( 'text-column', 0 )

    R['cmb:text' ].set_property( 'has-entry', False )
    R['cmb:int'  ].set_property( 'has-entry', False )
    R['cmb:float'].set_property( 'has-entry', False )


    R['val:int'  ].set_property( 'adjustment', gtk.Adjustment(0,0,100,1,10,0) )
    R['val:float'].set_property( 'adjustment', gtk.Adjustment(0,0,100,1,10,0) )

    R['val:int'  ].connect('editing-started', set_range, model)
    R['val:float'].connect('editing-started', set_range, model)

    R['cmb:text'].connect( 'editing-started', load_combobox, model )
    R['cmb:int'].connect( 'editing-started', load_combobox, model )
    R['cmb:float'].connect( 'editing-started', load_combobox, model )



    sheet_cb.connect_column(
      R['val:bool'],
      toggleitem=(helpers.toggle_item, model, model.VAL_BOOL, add_undo) )

    sheet_cb.connect_column(
      R['val:text'],
      setitem=(helpers.set_item, model, model.VAL_STR, add_undo) )

    sheet_cb.connect_column(
      R['val:int'],
      setitem=(helpers.set_item, model, model.VAL_INT, add_undo, False, int) )

    sheet_cb.connect_column(
      R['val:float'],
      setitem=(helpers.set_item, model, model.VAL_FLOAT, add_undo, False, float) )

    sheet_cb.connect_column(
      R['cmb:text'],
      setitem=(helpers.set_item, model, model.VAL_STR, add_undo) )

    sheet_cb.connect_column(
      R['cmb:int'],
      setitem=(helpers.set_item, model, model.VAL_INT, add_undo, False, int) )

    sheet_cb.connect_column(
      R['cmb:float'],
      setitem=(helpers.set_item, model, model.VAL_FLOAT, add_undo, False, float) )


    C = {
      'L' : gtk.TreeViewColumn('Parameter', R['label'], text=0),
      'V' : gtk.TreeViewColumn('Value'),
    }
    C['L'].set_flags(gtk.CAN_FOCUS)
    C['V'].set_flags(gtk.CAN_FOCUS)
    C['V'].pack_start(R['val:bool'])
    C['V'].pack_start(R['val:text'])
    C['V'].pack_start(R['val:int'])
    C['V'].pack_start(R['val:float'])
    C['V'].pack_start(R['cmb:text'])
    C['V'].pack_start(R['cmb:int'])
    C['V'].pack_start(R['cmb:float'])
    C['V'].set_attributes( R['val:bool'],   active=model.VAL_BOOL )
    C['V'].set_attributes( R['val:text'],   text=model.VAL_STR )
    C['V'].set_attributes( R['val:int'],    text=model.VAL_INT )
    C['V'].set_attributes( R['val:float'],  text=model.VAL_FLOAT )
    C['V'].set_attributes( R['cmb:text'],   text=model.VAL_STR )
    C['V'].set_attributes( R['cmb:int'],    text=model.VAL_INT )
    C['V'].set_attributes( R['cmb:float'],  text=model.VAL_FLOAT )

    def is_sensitive( treecol, cell, model, i, TYPE ):
      combo = False
      if type(TYPE) in [list,tuple]:
        TYPE, combo = TYPE

      show = model[i][model.TYPE] is TYPE

      # if range is list/tuple or callable, this entry needs a combo box
      # if this entry needs a combo box and this cell is not a combo box, set
      # show to False
      RANGE = model[i][model.RANGE]
      if show and ( type(RANGE) in [list, tuple] or callable(RANGE) ) != combo:
        show = False

      cell.set_property('sensitive', show)
      cell.set_property('visible', show)


    C['V'].set_cell_data_func( R['val:bool'],   is_sensitive, bool        )
    C['V'].set_cell_data_func( R['val:text'],   is_sensitive, str         )
    C['V'].set_cell_data_func( R['val:int'],    is_sensitive, int         )
    C['V'].set_cell_data_func( R['val:float'],  is_sensitive, float       )
    C['V'].set_cell_data_func( R['cmb:text'],   is_sensitive,(str,   True))
    C['V'].set_cell_data_func( R['cmb:int'],    is_sensitive,(int,   True))
    C['V'].set_cell_data_func( R['cmb:float'],  is_sensitive,(float, True))

    V.append_column(C['L'])
    V.append_column(C['V'])
    V.show()

if __name__ == '__main__':
  model = gtk.TreeStore( str, object, object, bool, str, int, float )
  model.LABEL     = 0
  model.TYPE      = 1
  model.RANGE     = 2
  model.VAL_BOOL  = 3
  model.VAL_STR   = 4
  model.VAL_INT   = 5
  model.VAL_FLOAT = 6
  model.to_index = {
    bool : model.VAL_BOOL,
    str  : model.VAL_STR,
    int  : model.VAL_INT,
    float: model.VAL_FLOAT,
  }

  def intlist():
    return [ (42, 'Answer to the universe'), (-42, 'Other universe?'), 10212 ]

  # valid range values:
  #   xrange object (valid for integer _and_ float types)
  #   any object that supports min(), max(), 'in' and 'not in'
  #   list/tuple of combo box entries. combo box entries can either be a simple
  #   value or a value/label pair.  For example:
  #     [ (0, 'a Zero value'),
  #       1,
  #       (2, 'Another nice value'),
  #     ]
  #   _OR_:  combo box range object can be a callable that returns list/tuple

  #                   # label  type  range         bool   str int  flt
  dev1 = \
  model.append(None, ('Dev1',  None, None,         False, '',  0,  0.0) )
  grp1 = \
  model.append(dev1, ('group0',None, None,         False, '',  0,  0.0) )

  model.append(grp1, ('param0',int,  xrange(11),   False, '',  10, 0.0) )
  model.append(grp1, ('param1',bool, None,         True,  '',  42, 0.0) )
  model.append(grp1, ('param2',float,xrange(-3,10),False, '',  42, 0.5) )
  model.append(grp1, ('param3',str,  None,         False, 'A', 0,  0) )
  model.append(grp1, ('intlst',int,  [(0,'zero'),
                                      5,
                                      (10,'ten')], False, '', 0,  0) )

  grp2 = \
  model.append(dev1, ('group0',None, None,         False, '',  0,  0.0) )

  model.append(grp2, ('fltlst',float,[(0,'zero'),
                                      5,
                                      (10,'ten')], False, '', 0,  0) )
  model.append(grp2, ('strlst',str,  [('zero',0),
                                      'five',
                                      ('ten','10')], False, '-', 0,  0) )
  model.append(grp2, ('intflst',int,  intlist,      False, '', 0,  0) )
  g = Generic(model)

  window = gtk.Window()
  window.connect('destroy', lambda e: gtk.main_quit())
  window.set_default_size(300,300)
  window.add(g.view)
  window.show()
  gtk.main()
