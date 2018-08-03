# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk, Gdk as gdk, GObject as gobject

class keys:
  LEFT  = 65361
  UP    = 65362
  RIGHT = 65363
  DOWN  = 65364
  ENTRY = 65293
  TAB   = 65289
  RTAB  = 65056
  BACKSP= 65288
  DEL   = 65535
  INSERT= 65379

  n     = gdk.KEY_n
  p     = gdk.KEY_p
  f     = gdk.KEY_f
  b     = gdk.KEY_b
  k     = gdk.KEY_k

  emacs = {
    n : (ENTRY,0),
    p : (ENTRY,gdk.ModifierType.SHIFT_MASK),
    f : (TAB,0),
    b : (RTAB,0),
  }

def change_event(event, bindings):
  k = event.keyval
  event.keyval = bindings[k][0]
  event.state |= bindings[k][1]


class Callbacks:

  def __init__(self, treeview, default=None):
    self.treeview = treeview
    self.default = default
    self.has_error = False
    self.prechars = str()

    self.connect_treeview()

    self.onclean = dict()


  def connect(self, sig, *args, **kwargs):
    if sig == 'clean':
      assert callable(args[0])
      assert callable(args[1])
      self.onclean['start'] = args[0]
      self.onclean['stop'] = args[1]
      self.onclean['args'] = args[2:]
      self.onclean['kwargs'] = kwargs
    else:
      raise NameError('unknown signal connection requested')

  def test_error(self):
    retval = self.has_error
    self.has_error = False
    return retval

  def set_error(self):
    self.has_error = True

  def add_row(self):
    model = self.treeview.get_model()
    model.append(self.default)

  def entry_pressed( self, entry, event ):
    if self.test_error():  return
    assert event.keyval == keys.ENTRY
    path, column = self.treeview.get_cursor()
    model = self.treeview.get_model()

    if path is None and len(model) == 0 and self.default:
      self.add_row()
      path = (0,)
      column = self.treeview.get_column(0)
    elif event.state & gdk.ModifierType.SHIFT_MASK and path[0]>0:
      path = (path[0]-1,)
    elif not (event.state & gdk.ModifierType.SHIFT_MASK):
      if path[0] < (len(model)-1):
        path = (path[0]+1,)
      elif self.default:
        self.add_row()
        self.entry_pressed(entry, event)
        return
    else:
      return

    gobject.timeout_add(100, lambda t, p, c: t.set_cursor(p, c),
                        self.treeview, path, column)


  def tab_pressed( self, entry, event ):
    if self.test_error():  return
    assert event.keyval in [ keys.TAB, keys.RTAB ]
    path, column = self.treeview.get_cursor()
    model = self.treeview.get_model()
    cols = self.treeview.get_columns()
    if column:
      col_i = cols.index(column)

    if path is None and len(model) == 0 and self.default:
      self.add_row()
      path = (0,)
      col_i = 0
    elif event.keyval == keys.RTAB:
      col_i -= 1
      if col_i < 0:
        col_i = len(cols) -1
        path = (path[0]-1,)
    elif event.keyval == keys.TAB:
      col_i += 1
      if col_i >= len(cols):
        col_i = 0
        path = (path[0]+1,)
    else:
      return
    column = cols[ col_i ]
    if path[0] >=0 and path[0] <= (len(model)-1):
      gobject.timeout_add(100, lambda t, p, c: t.set_cursor(p, c),
                          self.treeview, path, column)
    elif self.default and path[0] >= len(model):
      self.add_row()
      self.tab_pressed(entry, event)
      return

  def keypress_cb(self, entry, event):
      if event.keyval in [keys.UP, keys.DOWN]:
        return True
      elif event.keyval == keys.ENTRY:
        entry.activate()
        self.entry_pressed( entry, event )
        return True

      elif event.keyval in [ keys.TAB, keys.RTAB ]:
        entry.activate()
        self.tab_pressed( entry, event )
        return True

      return False

  def tv_keypress_cb(self, entry, event):
    if event.keyval in [ keys.p, keys.n, keys.f, keys.b ] and \
         event.state & gdk.ModifierType.CONTROL_MASK:
      change_event( event, keys.emacs )

    if event.keyval == keys.ENTRY:
      self.entry_pressed( entry, event )
      return True

    elif event.keyval in [ keys.TAB, keys.RTAB ]:
      self.tab_pressed( entry, event )
      return True

    elif self.default and \
         event.state & gdk.ModifierType.CONTROL_MASK and event.keyval == keys.k:
      if self.onclean:
        self.onclean['start'](*self.onclean['args'], **self.onclean['kwargs'])
      cleanlist = list()
      def cleanup(model, path, iter):
        if tuple(model[iter]) == tuple(self.default):
          cleanlist.append( gtk.TreeRowReference.new(model,path) )

      m = self.treeview.get_model()
      m.foreach( cleanup )
      for r in cleanlist:
        m.remove(m.get_iter(r.get_path()))
      if self.onclean:
        self.onclean['stop'](*self.onclean['args'], **self.onclean['kwargs'])
      return True

    elif self.default and event.keyval == keys.BACKSP:
      model, rows = self.treeview.get_selection().get_selected_rows()
      for p in rows:
        r = model[p]
        for j in range(len(self.default)):
          r[j] = self.default[j]
      return True

    elif event.keyval == keys.DEL:
      model, rows = self.treeview.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      rows = [ gtk.TreeRowReference.new(model, p)  for p in rows ]
      for r in rows:
        model.remove( model.get_iter( r.get_path() ) )
      return True

    elif event.keyval < 256 and len(self.treeview.get_model()):
      path, column = self.treeview.get_cursor()
      gobject.timeout_add(20, lambda t, p, c: t.set_cursor(p, c, True),
                          self.treeview, path, column)
      self.prechars += chr( event.keyval )
      return True

    return False

  def start_edit( self, cell, editable, path,
                  callback=None, *cbargs, **cbkwargs):
    if callback:
      callback( cell, editable, path, *cbargs, **cbkwargs )

    if self.prechars:
      editable.set_text( self.prechars )
      self.prechars = ''
      gobject.timeout_add(20, lambda e: e.select_region( 1,-1 ), editable)
    editable.connect('key-press-event', self.keypress_cb)

  def finished_edit( self, renderer, path, new_text, set_item, *args, **kwargs):
    try:
      set_item(renderer, path, new_text, *args, **kwargs)
    except Exception as e:
      print(e)
      self.set_error()


  def connect_column( self, c, setitem=None, toggleitem=None, startedit=None ):
    ids = list()
    assert not ( setitem and toggleitem ), 'Use only one of setitem/toggleitem!'

    if toggleitem:
      ids.append( c.connect('toggled', toggleitem[0], *toggleitem[1:] ) )
      return

    if startedit:
      assert callable(startedit[0]), 'Expected callable startedit[0] function'
      ids.append( c.connect('editing-started', self.start_edit, *startedit) )
    else:
      ids.append( c.connect('editing-started', self.start_edit) )

    if setitem:
      assert callable( setitem[0] ), 'Expected callable setitem[0] function'
      ids.append(
        c.connect('edited', self.finished_edit, setitem[0], *setitem[1:])
      )

    return ids


  def connect_treeview(self):
    self.treeview.connect('key-press-event', self.tv_keypress_cb)






def set_item( renderer, path, new_text, col, treeview):
  val = lambda v : v
  if col == 1:
    val = lambda v: eval(v)
  treeview.get_model()[path][col] = val(new_text)

def toggle_item( cell, path, col, treeview ):
  treeview.get_model()[path][col] ^= True


def test():
    model = gtk.ListStore(str, int, bool)
    model.append(['foo1', 23, True])
    model.append(['foo2', 24, True])
    model.append(['foo3', 25, True])

    treeView = gtk.TreeView(model)
    treeView.set_property( 'rules-hint', True )
    sheet_cb = Callbacks(treeView, ('',0, True))
    R = {
      'col0' : gtk.CellRendererText(),
      'col1' : gtk.CellRendererText(),
    }
    sheet_cb.connect_column( R['col0'], setitem=(set_item, 0, treeView) )
    sheet_cb.connect_column( R['col1'], setitem=(set_item, 1, treeView) )

    C = {
      'col0' : gtk.TreeViewColumn('Col0', R['col0'], text=0, editable=2),
      'col1' : gtk.TreeViewColumn('Col1', R['col1'], text=1, editable=2),
    }
    C['col0'].set_clickable(True)
    C['col1'].set_clickable(True)

    treeView.append_column(C['col0'])
    treeView.append_column(C['col1'])
    treeView.show()

    window = gtk.Window()
    window.connect('destroy', lambda e: gtk.main_quit())
    window.set_default_size(300,300)
    window.add(treeView)
    window.show()
    gtk.main()

if __name__ == '__main__':
    test()
