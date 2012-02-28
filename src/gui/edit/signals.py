# vim: ts=2:sw=2:tw=80:nowrap
import gtk
from helpers import *

def create(signals):
  SOURCE  =0
  DEST    =1
  INVERT  =2

  signal_editor = {
    'view'      : gtk.TreeView( signals ),
    'renderers' : {
      'source'  : gtk.CellRendererText(),
      'dest'    : gtk.CellRendererText(),
      'invert'  : gtk.CellRendererToggle(),
    },
  }
  R = signal_editor['renderers']

  R['source'].set_property( 'editable', True )
  R['dest'  ].set_property( 'editable', True )
  R['invert'].set_property( 'activatable', True )
  R['source'].connect( 'edited', set_item, signals, SOURCE )
  R['dest'  ].connect( 'edited', set_item, signals, DEST   )
  R['invert'].connect( 'toggled', set_item, signals, INVERT )

  signal_editor.update({
    'columns' : {
      'source'  : GTVC( 'Source',         R['source'],text=SOURCE ),
      'dest'    : GTVC( 'Destination',    R['dest'],  text=DEST ),
      'invert'  : GTVC( 'Invert Polarity',R['invert'],text=INVERT ),
    },
  })

  C = signal_editor['columns']
  V = signal_editor['view']
  C['invert'].add_attribute( R['invert'], 'active', INVERT )
  V.set_property( 'hover_selection', True )
  V.append_column( C['source'] )
  V.append_column( C['dest'] )
  V.append_column( C['invert'] )
  return signal_editor

