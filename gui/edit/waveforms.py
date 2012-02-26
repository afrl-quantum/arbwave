# vim: ts=2:sw=2:tw=80:nowrap
import gtk

from helpers import *

def load_channels_combobox( cell, editable, path, channels ):
  chls = gtk.ListStore(int,str)
  for i in xrange( len(channels) ):
    chls.append( [i, str(i) + ': ' + channels[i][0]] )

  editable.set_property("model", chls)

def create(waveforms,channels):
  CHANNEL =0
  TIME    =1
  VALUE   =2
  ENABLE  =3

  waveform_editor = {
    'view'      : gtk.TreeView( waveforms ),
    'renderers' : {
      'channel' : gtk.CellRendererCombo(),
      'time'    : gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    },
  }
  R = waveform_editor['renderers']
  waveform_editor.update({
    'columns' : {
      'channel' : GTVC( 'Channel', R['channel'], text=CHANNEL ),
      'time'    : GTVC( 'Time',    R['time'],    text=TIME ),
      'value'   : GTVC( 'Value',   R['value'],   text=VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'],  text=ENABLE ),
    },
  })

  R['channel'].set_property( 'editable', True )
  R['channel'].set_property("text-column", 1)
  R['channel'].connect( 'edited', set_item, waveforms, CHANNEL )
  R['channel'].connect( 'editing-started', load_channels_combobox, channels )

  R['time'].set_property( 'editable', True )
  R['time'].connect( 'edited', set_item, waveforms, TIME )

  R['value'].set_property( 'editable', True )
  R['value'].connect( 'edited', set_item, waveforms, VALUE )

  R['enable'].set_property( 'activatable', True )
  R['enable'].connect( 'toggled', toggle_item, waveforms, ENABLE )

  C = waveform_editor['columns']
  V = waveform_editor['view']
  C['enable'].add_attribute( R['enable'], 'active', ENABLE )
  V.set_property( 'hover_selection', True )
  V.append_column( C['channel'] )
  V.append_column( C['time'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )

  return waveform_editor

