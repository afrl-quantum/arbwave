# vim: ts=2:sw=2:tw=80:nowrap
import gtk

def GTVC(*args,**kwargs):
  c = gtk.TreeViewColumn(*args,**kwargs)
  c.set_property('resizable', True)
  return c


def set_item( cell, path, new_item, model, ITEM ):
  model[path][ITEM] = new_item

def toggle_item( cell, path, model, ITEM ):
  """
  Sets the toggled state on the toggle button to true or false.
  """
  model[path][ITEM] = not model[path][ITEM]

