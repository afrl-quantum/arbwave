# vim: ts=2:sw=2:tw=80:nowrap
import gtk
from helpers import *

from ... import backend

device_combobox_tree = gtk.TreeStore(str,str)

def build_device_combobox_tree():
  global device_combobox_tree
  T = device_combobox_tree
  T.clear()

  add_paths_to_combobox_tree( T, backend.get_routable_backplane_signals() )



def load_signals_combobox( cell, editable, path ):
  global device_combobox_tree
  if len(device_combobox_tree) < 1:
    build_device_combobox_tree()
  editable.set_property("model", device_combobox_tree)
  prep_combobox_for_tree(editable)


def create(signals):
  signal_editor = {
    'view'      : gtk.TreeView( signals ),
    'renderers' : {
      'source'  : gtk.CellRendererCombo(),
      'dest'    : gtk.CellRendererCombo(),
      'invert'  : gtk.CellRendererToggle(),
    },
  }
  R = signal_editor['renderers']

  R['source'].set_property( 'editable', True )
  R['dest'  ].set_property( 'editable', True )
  R['invert'].set_property( 'activatable', True )
  R['source'].set_property( 'text-column', 0 )
  R['dest'  ].set_property( 'text-column', 0 )
  R['source'].connect( 'edited', set_item, signals, signals.SOURCE )
  R['source'].connect( 'editing-started', load_signals_combobox )
  R['dest'  ].connect( 'edited', set_item, signals, signals.DEST   )
  R['dest'  ].connect( 'editing-started', load_signals_combobox )
  R['invert'].connect( 'toggled', toggle_item, signals, signals.INVERT )

  signal_editor.update({
    'columns' : {
      'source'  : GTVC( 'Source',         R['source'],text=signals.SOURCE ),
      'dest'    : GTVC( 'Destination',    R['dest'],  text=signals.DEST ),
      'invert'  : GTVC( 'Invert Polarity',R['invert'] ),
    },
  })

  C = signal_editor['columns']
  V = signal_editor['view']
  C['invert'].add_attribute( R['invert'], 'active', signals.INVERT )
  #V.set_property( 'hover_selection', True )
  V.append_column( C['source'] )
  V.append_column( C['dest'] )
  V.append_column( C['invert'] )
  return signal_editor

