# vim: ts=2:sw=2:tw=80:nowrap
import gtk

from helpers import *
from ... import backend

def load_devices_combobox( cell, editable, path ):
  devls = gtk.ListStore(str)
  for i in backend.analog:
    devls.append( [i] )
  for i in backend.digital:
    devls.append( [i] )
  editable.set_property("model", devls)

def create(channels):
  LABEL   =0
  DEVICE  =1
  VALUE   =2
  ENABLE  =3

  channel_editor = {
    'view'      : gtk.TreeView( channels ),
    'renderers' : {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    },
  }
  R = channel_editor['renderers']
  channel_editor.update({
    'columns' : {
      'label'   : GTVC( 'Label',   R['label'],    text=LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=DEVICE ),
      'value'   : GTVC( 'Value',   R['value'],  text=VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'], text=ENABLE ),
    },
  })

  R['label'].set_property( 'editable', True )
  R['label'].connect( 'edited', set_item, channels, LABEL )

  R['device'].set_property( 'editable', True )
  R['device'].set_property("text-column", 1)
  R['device'].connect( 'edited', set_item, channels, DEVICE )
  R['device'].connect( 'editing-started', load_devices_combobox )

  R['value'].set_property( 'editable', True )
  R['value'].connect( 'edited', set_item, channels, VALUE )

  R['enable'].set_property( 'activatable', True )
  R['enable'].connect( 'toggled', toggle_item, channels, ENABLE )

  C = channel_editor['columns']
  V = channel_editor['view']
  C['enable'].add_attribute( R['enable'], 'active', ENABLE )
  V.set_property( 'hover_selection', True )
  V.append_column( C['label'] )
  V.append_column( C['device'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )
  return channel_editor

