# vim: ts=2:sw=2:tw=80:nowrap
import gtk

def GTVC(*args,**kwargs):
  c = gtk.TreeViewColumn(*args,**kwargs)
  c.set_property('resizable', True)
  return c


def set_item( cell, path, new_item, model, ITEM, unique=False ):
  """
    if unique is True, this searches through the immediate chlidren for
      duplicate names before allowing the edit.
  """
  if not unique:
    model[path][ITEM] = new_item
  else:
    i = model.get_iter_first()
    for i in iter(model):
      if ( (type(path) is str and \
            model.get_string_from_iter(i.iter) != path ) or \
           (type(path) != str and i.path != path ) ) and \
           i[ITEM] == new_item:
        print 'Please use unique labels'
        return
    model[path][ITEM] = new_item

def toggle_item( cell, path, model, ITEM ):
  """
  Sets the toggled state on the toggle button to true or false.
  """
  model[path][ITEM] = not model[path][ITEM]



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

def add_paths_to_combobox_tree( T, P, category=None, M=None ):
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
  """
  if category is None:
    CAT = []
  else:
    CAT  = category.split('/')
  if M is None:
    M = dict()

  for c in P:
    add_path_to_combobox_tree( T, CAT + c.split('/'), len(CAT), M )

def prep_combobox_for_tree(cbox):
  # This ensures you can't select "Analog" or Dev2 instead of ni/Dev2/ao0
  def is_sensitive(celllayout, cell, model, i, *user_args):
    cell.set_property('sensitive', not model.iter_has_child(i))

  renderer = gtk.CellRendererText()
  cbox.clear()
  cbox.pack_start( renderer )
  cbox.add_attribute( renderer, 'text', 1 )
  cbox.set_cell_data_func( renderer, is_sensitive )
