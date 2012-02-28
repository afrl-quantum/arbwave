# vim: ts=2:sw=2:tw=80:nowrap
import gtk
from helpers import *

from ... import backend

def load_signals_combobox( cell, editable, path ):
  sigls = gtk.ListStore(str)
  for i in backend.backplane:
    sigls.append( [i] )
  editable.set_property("model", sigls)


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
  V.set_property( 'hover_selection', True )
  V.append_column( C['source'] )
  V.append_column( C['dest'] )
  V.append_column( C['invert'] )
  return signal_editor

