# vim: ts=2:sw=2:tw=80:nowrap
import gtk

def GTVC(*args,**kwargs):
  c = gtk.TreeViewColumn(*args,**kwargs)
  c.set_property('resizable', True)
  return c


class Undo:
  """Generic TreeModel Undo class"""
  def __init__(self, old_item, new_item, model, row, col):
    self.old_item = old_item
    self.new_item = new_item
    self.model    = model
    self.row      = row
    self.col      = col

  def undo(self):
    self.model[self.row][self.col] = self.old_item

  def redo(self):
    self.model[self.row][self.col] = self.new_item


def set_item( cell, path, new_item, model, ITEM, add_undo=None,
              unique=False, type=str ):
  """
    if unique is True, this searches through the immediate chlidren for
      duplicate names before allowing the edit.
  """
  new_item = type(new_item)
  if unique:
    i = model.get_iter_first()
    for i in iter(model):
      if ( (type(path) is str and \
            model.get_string_from_iter(i.iter) != path ) or \
           (type(path) != str and i.path != path ) ) and \
           i[ITEM] == new_item:
        print 'Please use unique labels'
        return

  if model[path][ITEM] == new_item:
    return  # avoid triggering a change if there is not actually a change

  if add_undo is not None:
    add_undo( Undo(model[path][ITEM], new_item, model, path, ITEM) )
  model[path][ITEM] = new_item

def toggle_item( cell, path, model, ITEM, add_undo=None ):
  """
  Sets the toggled state on the toggle button to true or false.
  """
  if add_undo is not None:
    add_undo( Undo(model[path][ITEM], not model[path][ITEM], model, path, ITEM) )
  model[path][ITEM] ^= True



def add_path_to_combobox_tree(T, p, k, M):
  """
    Add a device path to the gtk.TreeStore in T.

    T : The gtk.TreeStore instance

    p : path broken up as ['path', 'to', 'device']

    k : Number of elements to skip when setting string to be used for column 1.

    M : dictionary that maps 'path/to/device' to tree node.  This is for
        parenting subsequent nodes properly.
  """
  for i in xrange(len(p)):
    si = '/'.join(p[0:(i+1)])
    if si not in M:
      if i == 0:
        M[si] = T.append( None, (p[0], p[0]) )
      else:
        M[si] = T.append( M['/'.join(p[0:i])], ('/'.join(p[k:(i+1)]), p[i]) )

def add_paths_to_combobox_tree( T, P, category=None, M=None, skip_CAT=None ):
  """
    Add a set of paths to the gtk.TreeStore in T.

    T : The gtk.TreeStore instance

    P : The set of paths as 'path/to/device'

    category : A subcategory to which these set of paths should be organized.
        [OPTIONAL]

    M : dictionary that maps 'path/to/device' to tree node.  This is for
        parenting subsequent nodes properly.  This is only necessary if you will
        call add_paths more than once for the same category.
        [OPTIONAL]

    skip_CAT : How many elmements of the category path should be skipped with
        assigning actual path values. This defaults to skipping all category
        path elements.
        [OPTIONAL]
  """
  if category is None:
    CAT = []
  else:
    CAT  = category.split('/')
  if M is None:
    M = dict()

  if skip_CAT is None:
    skip_CAT = len(CAT)

  P = list(P)
  P.sort()
  for c in P:
    add_path_to_combobox_tree( T, CAT + c.split('/'), skip_CAT, M )

def prep_combobox_for_tree(cbox):
  # This ensures you can't select "Analog" or Dev2 instead of ni/Dev2/ao0
  def is_sensitive(celllayout, cell, model, i, *user_args):
    cell.set_property('sensitive', not model.iter_has_child(i))

  renderer = gtk.CellRendererText()
  cbox.clear()
  cbox.pack_start( renderer )
  cbox.add_attribute( renderer, 'text', 1 )
  cbox.set_cell_data_func( renderer, is_sensitive )



popup_handlers = dict()

def popup_button_press_handler(treeview, event, ui_manager, popup, actions):
  global popup_handlers
  if event.button == 3:
    x = int(event.x)
    y = int(event.y)
    time = event.time
    pthinfo = treeview.get_path_at_pos(x, y)
    if pthinfo is not None:
      path, col, cellx, celly = pthinfo
      if len(path) == 1:
        treeview.grab_focus()
        treeview.set_cursor( path, col, 0)
        model = treeview.get_model()

        for a in actions:
          act = ui_manager.get_action(a[0])
          if a[0] in popup_handlers and popup_handlers[a[0]]:
            act.disconnect( popup_handlers[a[0]] )
          if a[1] == toggle_item:
            act.set_active( model[path][a[2]] )
          popup_handlers[a[0]] = \
            act.connect('activate', a[1], path, model, *a[2:])

        popup.popup( None, None, None, event.button, time )
    return True
