# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, Gdk as gdk
from math import log10
import spreadsheet
import helpers
from helpers import GTVC, GCRT

def get_leaf_node( D, path ):
  if len(path) > 1:
    return get_leaf_node( D[path[0]], path[1:] )
  else:
    return D.get(path[0],None)

def get_leaf_node_parameters( D, path ):
  if len(path) > 1:
    return get_leaf_node( D[path[0]]['parameters'], path[1:] )
  else:
    return D.get(path[0],None)


class Range:
  def __init__(self, template, cfg_path, use_enable):
    self.template = template
    self.cfg_path = cfg_path
    if use_enable:
      self.get_leaf_node = get_leaf_node_parameters
    else:
      self.get_leaf_node = get_leaf_node

    cfg = self.cfg()

    if cfg is None:
      self.doreload = False
      self.combo = False
      self.r = None
      return

    self.doreload = 'doreload' in cfg and cfg['doreload']
    r = cfg['range']
    if not self.doreload:
      self.r = r

    # if range is list/tuple or callable, this entry needs a combo box
    if 'combo' in cfg:
      self.combo = cfg['combo']
    else:
      self.combo = type(r) in [list, tuple]

  def cfg(self):
    """
    Return the full config item.
    """
    return self.get_leaf_node( self.template, self.cfg_path )

  def __call__(self):
    """
    Return the range.
    """
    if self.doreload:
      r = self.cfg()['range']
    else:
      r = self.r
    if callable(r):
      return r()
    else:
      return r

  def is_combo(self):
    return self.combo

  def __iter__(self):
    return iter(self())

  def get_adjustment(self):
    r = self()
    if type(r) is xrange:
      return r[0], r[-1], -1, -1
    else:
      if len(r) == 4:
        return r[0:4]
      return min(r), max(r), -1, -1


class RangeFactory:
  def __init__( self, template=dict(), use_enable=False ):
    self.template = template
    self.use_enable = use_enable

  def set_template(self, template):
    self.template = self.template

  def __call__( self, path, i, model ):
    return Range( self.template, path, self.use_enable )



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
  RANGE = row[model.RANGE]
  assert not RANGE.is_combo(), 'Generic.set_range called with tuple/list'

  mn, mx, step, page = RANGE.get_adjustment()
  TYPE = row[model.TYPE]

  editable.connect('activate', coerce_range, TYPE )

  if TYPE is int:
    if step == -1 and page == -1:
      step = 1
      page = max(1,.1*(mx-mn))
    adj.configure(row[model.VAL_INT], mn, mx, step, page, 0)
  elif TYPE is float:
    if step == -1 and page == -1:
      step = .01*(mx-mn)
      page = .1*(mx-mn)
    digits = int(round( -log10( step * 0.01 ) ))
    if digits > 0:
      editable.set_digits(digits)
    adj.configure(row[model.VAL_FLOAT], mn, mx, step, page, 0)
  else:
    raise RuntimeError('expected int or float')


def load_combobox( cell, editable, path, model ):
  L = gtk.ListStore( str, str )
  editable.set_model( L )
  RANGE = model[path][model.RANGE]
  assert RANGE.is_combo(), 'Generic.load_combobox called without tuple/list'

  for i in RANGE:
    if type(i) in [list,tuple]:
      L.append( (str(i[0]), '{}: {}'.format(i[0],i[1])) )
    else:
      L.append( (str(i), str(i)) )

  # set up to combo to display the label not the value
  editable.clear()
  renderer = gtk.CellRendererText()
  editable.pack_start( renderer, True )
  editable.add_attribute( renderer, 'text', 1 )


def get_config_path(path, model, CPath=None):
  if CPath is None:
    CPath = list()
  if len(path) > 1:
    get_config_path(path[:-1], model, CPath)
  CPath.append(model[path][model.LABEL])
  return CPath


def drag_motion(w, ctx, x, y, time):
  mask = w.window.get_pointer()[2]
  if mask & gdk.ModifierType.CONTROL_MASK:
    ctx.drag_status( gdk.DragAction.COPY, time )


class Generic:
  def __init__(self, model, add_undo=None,
               range_factory=RangeFactory(), template=None,
               reorderable=False,
               editable_label_prefixes=['External/']):
    self.add_undo = add_undo
    self.range_factory = range_factory
    self.editable_label_prefixes = editable_label_prefixes
    assert callable(range_factory), 'Generic.range_factory must be callable'
    if template is not None:
      self.range_factory.set_template( template )

    V = self.view = gtk.TreeView(model)
    V.set_property( 'rules-hint', True )
    sheet_cb = spreadsheet.Callbacks(V)
    enable = 'ENABLE' in dir(model)

    if reorderable:
      V.set_reorderable(True)
      V.connect('drag-motion', drag_motion)

    R = {
      'label'     : GCRT(),
      'val:bool'  : gtk.CellRendererToggle(),
      'val:text'  : GCRT(),
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
      R['label'],
      setitem=(helpers.set_item, model, model.LABEL, add_undo,
               False, str, self.editable_label_prefixes) )

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
      'L' : GTVC('Parameter', R['label'], text=0),
      'V' : GTVC('Value'),
    }
    C['L'].set_clickable(True)
    C['V'].set_clickable(True)
    C['V'].pack_start(R['val:bool'],True)
    C['V'].pack_start(R['val:text'],True)
    C['V'].pack_start(R['val:int'],True)
    C['V'].pack_start(R['val:float'],True)
    C['V'].pack_start(R['cmb:text'],True)
    C['V'].pack_start(R['cmb:int'],True)
    C['V'].pack_start(R['cmb:float'],True)
    C['V'].set_attributes( R['val:bool'],   active=model.VAL_BOOL )
    C['V'].set_attributes( R['val:text'],   text=model.VAL_STR )
    C['V'].set_attributes( R['val:int'],    text=model.VAL_INT )
    C['V'].set_attributes( R['val:float'],  text=model.VAL_FLOAT )
    C['V'].set_attributes( R['cmb:text'],   text=model.VAL_STR )
    C['V'].set_attributes( R['cmb:int'],    text=model.VAL_INT )
    C['V'].set_attributes( R['cmb:float'],  text=model.VAL_FLOAT )


    def can_edit(treecol, cell, model, i, data ):
      Ltxt = model[i][model.LABEL]
      if True in [ Ltxt.startswith(i) for i in self.editable_label_prefixes ]:
        cell.set_property('editable', True)
      else:
        cell.set_property('editable', False)

    C['L'].set_cell_data_func( R['label'], can_edit )

    def is_sensitive( treecol, cell, model, i, TYPE ):
      combo = False
      if type(TYPE) in [list,tuple]:
        TYPE, combo = TYPE

      show = model[i][model.TYPE] is TYPE

      if show:
        if model[i][model.RANGE] is None and self.range_factory is not None:
          # Create Range class
          model[i][model.RANGE] = \
            self.range_factory( get_config_path(model.get_path(i), model),
                                i, model )

        if combo != model[i][model.RANGE].is_combo():
          show = False
      if show and TYPE == float:
        cell.set_property('text', '%g' %  model[i][model.VAL_FLOAT])

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

    if enable:
      R['enable'] = gtk.CellRendererToggle()
      R['enable'].set_property('activatable', True)
      R['enable'].connect('toggled', helpers.toggle_item, model, model.ENABLE, add_undo)
      C['enable'] = GTVC('Enabled', R['enable'])
      C['enable'].add_attribute(R['enable'], 'active', model.ENABLE)
      V.append_column( C['enable'] )

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

  template = {
    'Dev1' : {
      'group0' : {
        'param0' : {'range':xrange(11)},
        'param2' : {'range':xrange(-3,10)},
        'intlst' : {'range':[(0,'zero'), 5, (10,'ten')]},
      },
      'group1' : {
        'fltlst' : {'range':[(0.5,'point 5'), 5.5, (10.5,'ten point five')]},
        'strlst' : {'range':[('zero',0), 'five', ('ten','10')]},
        'intflst': {'range':intlist, 'combo':True},
      },
    },
  }
  rf = RangeFactory(template)

  #                   # label  type  range         bool   str int  flt
  dev1 = \
  model.append(None, ('Dev1',  None, None, False, '',  0,  0.0) )
  grp1 = \
  model.append(dev1, ('group0',None, None, False, '',  0,  0.0) )

  model.append(grp1, ('param0',int,  None, False, '',  10, 0.0) )
  model.append(grp1, ('param1',bool, None, True,  '',  42, 0.0) )
  model.append(grp1, ('param2',float,None, False, '',  42, 0.5) )
  model.append(grp1, ('param3',str,  None,         False, 'A', 0,  0) )
  model.append(grp1, ('intlst',int,  None, False, '', 0,  0) )

  grp2 = \
  model.append(dev1, ('group1',None, None, False, '',  0,  0.0) )

  model.append(grp2, ('fltlst',float,None, False, '', 0,  0) )
  model.append(grp2, ('strlst',str,  None, False, '-', 0,  0) )
  model.append(grp2, ('intflst',int, None, False, '', 0,  0) )
  g = Generic(model, range_factory=rf)

  window = gtk.Window()
  window.connect('destroy', lambda e: gtk.main_quit())
  window.set_default_size(300,300)
  window.add(g.view)
  window.show()
  gtk.main()
