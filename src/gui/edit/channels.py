# vim: ts=2:sw=2:tw=80:nowrap
import gtk

from helpers import *
from ... import backend

device_combobox_tree = gtk.TreeStore(str,str)

def build_device_combobox_tree():
  global device_combobox_tree
  T = device_combobox_tree
  T.clear()

  add_paths_to_combobox_tree( T, backend.analog,  'Analog'  )
  add_paths_to_combobox_tree( T, backend.digital, 'Digital' )



def load_devices_combobox( cell, editable, path ):
  global device_combobox_tree
  if len(device_combobox_tree) < 1:
    build_device_combobox_tree()
  editable.set_property("model", device_combobox_tree)
  prep_combobox_for_tree(editable)



def query_tooltip(widget, x, y, keyboard_tip, tooltip):
  try:
    model, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    value = model.get(iter, 0)
    tooltip.set_markup("<b>Path %s:</b> %s" %(path[0], value[0]))
    widget.set_tooltip_row(tooltip, path)
    return True
  except:
    return False


class Channels:
  def __init__(self, channels, add_undo=None):
    self.add_undo = add_undo
    self.channels = channels

    V = self.view = gtk.TreeView( channels )

    R = {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
      'scaling' : gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    }

    R['label'].set_property( 'editable', True )
    R['label'].connect( 'edited', set_item,
                        channels, channels.LABEL, self.add_undo, True )

    R['device'].set_property( 'editable', True )
    R['device'].set_property("text-column", 0)
    R['device'].connect( 'edited', set_item,
                         channels, channels.DEVICE, self.add_undo )
    R['device'].connect( 'editing-started', load_devices_combobox )

    R['value'].set_property( 'editable', True )
    R['value'].connect( 'edited', set_item,
                        channels, channels.VALUE, self.add_undo )

    R['scaling'].set_property( 'editable', True )
    R['scaling'].connect( 'edited', set_item,
                          channels, channels.SCALING, self.add_undo )

    R['enable'].set_property( 'activatable', True )
    R['enable'].connect( 'toggled', toggle_item,
                          channels, channels.ENABLE, self.add_undo )

    C = {
      'label'   : GTVC( 'Label',   R['label'],  text=channels.LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=channels.DEVICE ),
      'scaling' : GTVC( 'Scaling', R['scaling'],text=channels.SCALING ),
      'value'   : GTVC( 'Value',   R['value'],  text=channels.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    }

    C['enable'].add_attribute( R['enable'], 'active', channels.ENABLE )

    #V.set_property( 'hover_selection', True )
    V.set_property( 'has_tooltip', True )
    V.connect('query-tooltip', query_tooltip)
    V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
    V.append_column( C['label'  ] )
    V.append_column( C['device' ] )
    V.append_column( C['scaling'] )
    V.append_column( C['value'  ] )
    V.append_column( C['enable' ] )


  def insert_row(self):
    i = self.channels.insert_before(self.view.get_selection().get_selected()[1])
    self.add_undo( ListUndo(i, self.channels) )

  def delete_row(self):
    i = self.view.get_selection().get_selected()[1]
    if i:
      n = self.channels.iter_next( i )
      self.add_undo( ListUndo(i, self.channels, deletion=True) )
      self.channels.remove( i )
      if n:
        self.view.get_selection().select_iter( n )


class ListUndo:
  def __init__(self, iter, model, deletion=False):
    self.model = model
    self.path = model.get_path( iter )
    self.position = self.path[0]
    self.new_row = list(model[iter])
    self.deletion = deletion

  def delete(self):
    self.model.remove( self.model.get_iter(self.path) )

  def insert(self):
    self.model.insert( self.position, self.new_row )

  def redo(self):
    if self.deletion: self.delete()
    else:             self.insert()

  def undo(self):
    if self.deletion: self.insert()
    else:             self.delete()
