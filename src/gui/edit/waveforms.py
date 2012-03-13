# vim: ts=2:sw=2:tw=80:nowrap
import gtk

from helpers import *

def load_channels_combobox( cell, editable, path, channels ):
  chls = gtk.ListStore(str)
  for i in iter(channels):
    chls.append([ i[channels.LABEL] ])

  editable.set_property("model", chls)

def create(waveforms,channels):
  waveform_editor = {
    'view'      : gtk.TreeView( waveforms ),
    'renderers' : {
      'channel' : gtk.CellRendererCombo(),
      'time'    : gtk.CellRendererText(),
      'duration': gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    },
  }
  R = waveform_editor['renderers']
  waveform_editor.update({
    'columns' : {
      'channel' : GTVC( 'Channel', R['channel'], text=waveforms.CHANNEL ),
      'time'    : GTVC( 'Time',    R['time'],    text=waveforms.TIME ),
      'duration': GTVC( 'Duration',R['duration'],text=waveforms.DURATION ),
      'value'   : GTVC( 'Value',   R['value'],   text=waveforms.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    },
  })

  R['channel'].set_property( 'editable', True )
  R['channel'].set_property('text-column', 0)
  R['channel'].set_property('has-entry', False)
  R['channel'].connect( 'edited', set_item, waveforms, waveforms.CHANNEL )
  R['channel'].connect( 'editing-started', load_channels_combobox, channels )

  R['time'].set_property( 'editable', True )
  R['time'].connect( 'edited', set_item, waveforms, waveforms.TIME )

  R['duration'].set_property( 'editable', True )
  R['duration'].connect( 'edited', set_item, waveforms, waveforms.DURATION )

  R['value'].set_property( 'editable', True )
  R['value'].connect( 'edited', set_item, waveforms, waveforms.VALUE )

  R['enable'].set_property( 'activatable', True )
  R['enable'].connect( 'toggled', toggle_item, waveforms, waveforms.ENABLE )

  C = waveform_editor['columns']
  V = waveform_editor['view']
  C['enable'].add_attribute( R['enable'], 'active', waveforms.ENABLE )
  #V.set_property( 'hover_selection', True )
  V.append_column( C['channel'] )
  V.append_column( C['time'] )
  V.append_column( C['duration'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )

  return waveform_editor

