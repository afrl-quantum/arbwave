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

def create(channels):
  channel_editor = {
    'view'      : gtk.TreeView( channels ),
    'renderers' : {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
      'scaling' : gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    },
  }
  R = channel_editor['renderers']
  channel_editor.update({
    'columns' : {
      'label'   : GTVC( 'Label',   R['label'],  text=channels.LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=channels.DEVICE ),
      'scaling' : GTVC( 'Scaling', R['scaling'],text=channels.SCALING ),
      'value'   : GTVC( 'Value',   R['value'],  text=channels.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    },
  })

  R['label'].set_property( 'editable', True )
  R['label'].connect( 'edited', set_item, channels, channels.LABEL, True )

  R['device'].set_property( 'editable', True )
  R['device'].set_property("text-column", 0)
  R['device'].connect( 'edited', set_item, channels, channels.DEVICE )
  R['device'].connect( 'editing-started', load_devices_combobox )

  R['value'].set_property( 'editable', True )
  R['value'].connect( 'edited', set_item, channels, channels.VALUE )

  R['scaling'].set_property( 'editable', True )
  R['scaling'].connect( 'edited', set_item, channels, channels.SCALING )

  R['enable'].set_property( 'activatable', True )
  R['enable'].connect( 'toggled', toggle_item, channels, channels.ENABLE )

  C = channel_editor['columns']
  V = channel_editor['view']
  C['enable'].add_attribute( R['enable'], 'active', channels.ENABLE )

  def query_tooltip(widget, x, y, keyboard_tip, tooltip):
    try:
      model, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
      value = model.get(iter, 0)
      tooltip.set_markup("<b>Path %s:</b> %s" %(path[0], value[0]))
      widget.set_tooltip_row(tooltip, path)
      return True
    except:
      return False


  #V.set_property( 'hover_selection', True )
  V.set_property( 'has_tooltip', True )
  V.connect('query-tooltip', query_tooltip)
  V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
  V.append_column( C['label'] )
  V.append_column( C['device'] )
  V.append_column( C['scaling'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )
  return channel_editor

