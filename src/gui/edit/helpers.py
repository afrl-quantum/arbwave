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

