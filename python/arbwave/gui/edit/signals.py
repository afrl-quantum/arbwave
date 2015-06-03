# vim: ts=2:sw=2:tw=80:nowrap
import gtk
from helpers import *

from ... import backend
from .. import hosts_changed

signal_combobox_tree = gtk.TreeStore(str,str)
dest_combobox_tree = dict()
dest_combobox_tree_all = gtk.TreeStore(str,str)
dest_to_sig_tree = dict()

def build_device_combobox_tree():
  global signal_combobox_tree, dest_combobox_tree, dest_to_sig_tree
  dest_to_sigs = dict()
  T = signal_combobox_tree
  T.clear()
  dest_combobox_tree.clear()
  dest_combobox_tree_all.clear()
  dest_to_sig_tree.clear()

  routes = backend.get_routeable_backplane_signals()
  add_paths_to_combobox_tree( T, [ r.src for r in routes ] )

  # now, for each routes, we will generate a list of destinations
  for r in routes:
    if r.src not in dest_combobox_tree:
      dest_combobox_tree[ r.src ] = gtk.TreeStore(str,str)
    add_paths_to_combobox_tree( dest_combobox_tree[ r.src ], r.dest )

    for dest in r.dest:
      if dest not in dest_to_sigs:
        dest_to_sigs[dest] = list()
      dest_to_sigs[dest].append( r.src )

  for dest in dest_to_sigs:
    T = gtk.TreeStore(str,str)
    add_paths_to_combobox_tree( T, dest_to_sigs[dest] )
    dest_to_sig_tree[dest] = T

  add_paths_to_combobox_tree(dest_combobox_tree_all, dest_to_sigs.keys())


hosts_changed.callbacks.append( build_device_combobox_tree )



def load_signals_combobox( cell, editable, path, model ):
  global signal_combobox_tree
  if len(signal_combobox_tree) < 1:
    build_device_combobox_tree()
  if model[path][model.DEST] in dest_to_sig_tree:
    editable.set_property('model', dest_to_sig_tree[model[path][model.DEST]])
  else:
    editable.set_property('model', signal_combobox_tree)
  prep_combobox_for_tree(editable)


def load_dest_combobox( cell, editable, path, model ):
  global signal_combobox_tree, dest_combobox_tree
  if len(signal_combobox_tree) < 1:
    build_device_combobox_tree()
  if model[path][model.SOURCE] in dest_combobox_tree:
    editable.set_property('model', dest_combobox_tree[model[path][model.SOURCE]])
  else:
    editable.set_property('model', dest_combobox_tree_all)
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
  R['source'].connect( 'editing-started', load_signals_combobox, signals )
  R['dest'  ].connect( 'edited', set_item, signals, signals.DEST   )
  R['dest'  ].connect( 'editing-started', load_dest_combobox, signals )
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

