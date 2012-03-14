# vim: ts=2:sw=2:tw=80:nowrap
import gtk, gobject

from helpers import *
from script import edit as do_script_edit

ui_info = \
"""<ui>
  <popup name='WFG:Edit'>
    <menuitem action='WFG:Async'/>
    <separator/>
    <menuitem action='WFG:Script'/>
  </popup>
</ui>"""

def edit_script(action, row, col, A, handler):
  row[col] = do_script_edit(text=row[col])[1]
  A.disconnect( handler['id'] )

def toggle_async(action, row, col, A, handler):
  row[col] = not row[col]
  A.disconnect( handler['id'] )

def create_action_group():
  # GtkActionEntry
  entries = (
    ( 'WFG:Script', None,               # name, stock id
      'Edit Local Script', None,        # label, accelerator
      'Edit local script'),             # tooltip
  )

  # GtkToggleActionEntry
  toggle_entries = (
    ( 'WFG:Async', None,                # name, stock id
      'Asynchronous', None,             # label, accelerator
      'Do not use for calculation of '
      "natural time 't' for subsequent "
      'waveform groups',                # tooltip
      None,                             # callback (will connect later)
      True ),                           # is_active
  )

  #     # Create the menubar and toolbar
  action_group = gtk.ActionGroup('ConfigActions')
  action_group.add_actions(entries)
  action_group.add_toggle_actions(toggle_entries)
  return action_group

def mkUIManager():
  merge = gtk.UIManager()
  merge.insert_action_group(create_action_group(), 0)
  try:
    mergeid = merge.add_ui_from_string(ui_info)
  except gobject.GError, msg:
    print 'building popup menu failed: ' + msg
  return merge

def load_channels_combobox( cell, editable, path, channels ):
  chls = gtk.ListStore(str)
  editable.set_property("model", chls)

  if not( len(path) == 1 and type(editable.child) is gtk.Entry ):
    editable.child.set_property('editable', False)
    for i in iter(channels):
      chls.append([ i[channels.LABEL] ])



def query_tooltip(widget, x, y, keyboard_tip, tooltip):
  try:
    waveforms, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    markup = ''
    sep = ''
    script, async = waveforms.get(iter, waveforms.SCRIPT, waveforms.ASYNC)

    if len(path) == 1: # group-only information
      if async is not None:
        desc = {
          True : 'will <u><b>not</b></u>',
          False: '<b>will</b>',
        }
        markup += sep + \
          '<b>Asynchronous:</b>  {a}\n' \
          '    Group {d} be used for calculation of \n' \
          "    natural time 't' for subsequent waveform groups" \
          ''.format(a=async,d=desc[async])
        sep = '\n'
      if script:
        markup += sep + \
          '<b>Script:</b>\n' \
          '<span size="small">{s}</span>' \
          .format(s=script)
        sep = '\n'

    tooltip.set_markup( markup )
    widget.set_tooltip_row(tooltip, path)
    return True
  except:
    return False


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
  R['channel'].set_property('has-entry', True)
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
  V.set_property( 'has_tooltip', True )
  V.connect('query-tooltip', query_tooltip)
  V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
  V.append_column( C['channel'] )
  V.append_column( C['time'] )
  V.append_column( C['duration'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )

  def button_press_handler(treeview, event, ui_manager, popup):
    if event.button == 3:
      x = int(event.x)
      y = int(event.y)
      time = event.time
      pthinfo = treeview.get_path_at_pos(x, y)
      if pthinfo is not None:
        path, col, cellx, celly = pthinfo
        if len(path) == 1:
          treeview.grab_focus()
          treeview.set_cursor( path, col, 0)
          waveforms = treeview.get_model()
          row = waveforms[path]

          # reset Async action
          async = ui_manager.get_action('/WFG:Edit/WFG:Async')
          async.set_active( row[waveforms.ASYNC] )
          handler = dict()
          handler['id'] = \
            async.connect('activate', toggle_async, row, waveforms.ASYNC,
                          async, handler)

          # reset Script action
          script = ui_manager.get_action('/WFG:Edit/WFG:Script')
          handler = dict()
          handler['id'] = \
            script.connect('activate', edit_script, row, waveforms.SCRIPT,
                           script, handler)

          popup.popup( None, None, None, event.button, time )
      return True

  ui_manager = mkUIManager()
  V.connect('button-press-event',
    button_press_handler,
    ui_manager,
    ui_manager.get_widget('/WFG:Edit') )

  return waveform_editor
