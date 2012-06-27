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

def edit_script(action, path, model, col, add_undo=None):
  model[path][col] = do_script_edit(text=model[path][col])[1]

def create_action_group():
  # GtkActionEntry
  entries = (
    ( 'WFG:Script', None,               # name, stock id
      'Local Script...', None,        # label, accelerator
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

def is_group( model, path ):
  return model.iter_has_child( model.get_iter(path) )

def load_channels_combobox( cell, editable, path, model, channels ):
  chls = gtk.ListStore(str)
  editable.set_property("model", chls)
  chls.append(('',)) # add a blank line to allow selection of 'empty' channel

  # ensure that group-level items edit text and do not use drop down
  if not( is_group(model, path) and type(editable.child) is gtk.Entry ):
    editable.child.set_property('editable', False)
    for i in iter(channels):
      chls.append([ i[channels.LABEL] ])

def allow_value_edit( cell, editable, path, model ):
  """Ensure that group-level items cannot edit value"""
  assert type(editable) is gtk.Entry, 'value type is not gtk.Entry(?)!'
  if is_group( model, path ):
    editable.set_property('editable', False)



def query_tooltip(widget, x, y, keyboard_tip, tooltip):
  try:
    waveforms, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    markup = ''
    sep = ''
    script, async = waveforms.get(iter, waveforms.SCRIPT, waveforms.ASYNC)

    if is_group( waveforms, path ): # group-only information
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



def begin_drag(w, ctx, parent):
  # pause updates because of waveform updates
  parent.pause()

def drag_motion(w, ctx, x, y, time, parent):
  mask = w.window.get_pointer()[2]
  if mask & gtk.gdk.CONTROL_MASK:
    ctx.drag_status( gtk.gdk.ACTION_COPY, time )

def end_drag(w, ctx, parent, waveforms):
  # unpause updates and force an update based on waveform changes
  parent.unpause()
  parent.update(waveforms)


def gather_paths(channels, wvfms, i):
  L = list()
  dev = None
  for c in iter(channels):
    if wvfms[i][wvfms.CHANNEL] == c[channels.LABEL]:
      dev = c[channels.DEVICE]
  if dev:
    L.append( (wvfms.get_path(i), dev.partition('/')[-1]) )
  if wvfms.iter_has_child(i):
    child = wvfms.iter_children(i)
    while child:
      L += gather_paths(channels, wvfms, child)
      child = wvfms.iter_next( child )
  return L


def highlight(selection, plotter, channels):
  model, i = selection.get_selected()
  if i:
    paths = gather_paths( channels, model, i )
    plotter.highlight_parts( paths )
  else:
    plotter.highlight_parts( list() )


def clear_selection(w, event):
  if event.keyval == 65307:
    sel = w.get_selection()
    if sel.get_selected()[1]:
      sel.unselect_all()
    else:
      w.parent.grab_focus()



class Waveforms:
  def __init__(self, waveforms, channels, parent, add_undo=None):
    self.add_undo = add_undo
    self.waveforms = waveforms
    self.parent = parent

    V = self.view = gtk.TreeView( waveforms )
    V.set_reorderable(True)
    V.connect('drag-begin', begin_drag, parent)
    V.connect('drag-end', end_drag, parent, waveforms)
    V.connect('drag-motion', drag_motion, parent)
    V.get_selection().connect('changed',highlight,self.parent.plotter,channels)
    V.connect('key-press-event', clear_selection)

    R = {
      'channel' : gtk.CellRendererCombo(),
      'time'    : gtk.CellRendererText(),
      'duration': gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    }

    R['channel'].set_property( 'editable', True )
    R['channel'].set_property('text-column', 0)
    R['channel'].set_property('has-entry', True)
    R['channel'].connect( 'edited', set_item,
                          waveforms, waveforms.CHANNEL, self.add_undo )
    R['channel'].connect( 'editing-started', load_channels_combobox,
                          waveforms, channels )

    R['time'].set_property( 'editable', True )
    R['time'].connect( 'edited', set_item,
                       waveforms, waveforms.TIME, self.add_undo )

    R['duration'].set_property( 'editable', True )
    R['duration'].connect( 'edited', set_item,
                           waveforms, waveforms.DURATION, self.add_undo )

    R['value'].set_property( 'editable', True )
    R['value'].connect( 'edited', set_item,
                        waveforms, waveforms.VALUE, self.add_undo )
    R['value'].connect( 'editing-started', allow_value_edit, waveforms )

    R['enable'].set_property( 'activatable', True )
    R['enable'].connect( 'toggled', toggle_item,
                         waveforms, waveforms.ENABLE, self.add_undo )

    C = {
      'channel' : GTVC( 'Channel', R['channel'], text=waveforms.CHANNEL ),
      'time'    : GTVC( 'Time',    R['time'],    text=waveforms.TIME ),
      'duration': GTVC( 'Duration',R['duration'],text=waveforms.DURATION ),
      'value'   : GTVC( 'Value',   R['value'],   text=waveforms.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    }

    C['enable'].add_attribute( R['enable'], 'active', waveforms.ENABLE )

    V.set_property( 'hover_selection', True )
    V.set_property( 'has_tooltip', True )
    V.connect('query-tooltip', query_tooltip)
    V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
    V.append_column( C['channel'  ] )
    V.append_column( C['time'     ] )
    V.append_column( C['duration' ] )
    V.append_column( C['value'    ] )
    V.append_column( C['enable'   ] )

    ui_manager = mkUIManager()
    V.connect('button-press-event',
      popup_button_press_handler,
      is_group,
      ui_manager,
      ui_manager.get_widget('/WFG:Edit'),
      [('/WFG:Edit/WFG:Async', toggle_item,  waveforms.ASYNC,  self.add_undo),
       ('/WFG:Edit/WFG:Script', edit_script, waveforms.SCRIPT, self.add_undo)],
    )



  def insert_waveform(self):
    self.parent.pause()
    i = self.view.get_selection().get_selected()[1]
    if not i: # append new element to last group
      n = self.waveforms.append( None, self.waveforms.default_element )
    else: # insert into group before selected item
      iter = self.waveforms[i].iter
      p = self.waveforms[i].parent
      if p: pi = p.iter
      else: pi = None
      n = self.waveforms.insert_before(pi, iter, self.waveforms.default_element)
    self.view.expand_to_path( self.waveforms[n].path )

    self.add_undo( TreeUndo(n, self.waveforms, self.view) )
    self.parent.unpause()
    self.parent.update(self.waveforms)



  def delete_row(self):
    i = self.view.get_selection().get_selected()[1]
    if i:
      n = self.waveforms.iter_next( i )
      self.add_undo( TreeUndo(i, self.waveforms, self.view, deletion=True) )
      self.waveforms.remove( i )
      if n:
        self.view.get_selection().select_iter( n )


class NullUndo:
  def undo(self):
    pass
  def redo(self):
    pass

class TreeUndo:
  def __init__(self, iter, model, view, deletion=False):
    self.model = model
    self.view = view
    self.path = model.get_path( iter )
    self.position = self.path[-1]
    self.parent_path = self.path[:-1]
    self.new_row = list(model[iter])
    self.deletion = deletion

  def delete(self):
    self.model.remove( self.model.get_iter(self.path) )

  def insert(self):
    if self.parent_path:
      parent = self.model.get_iter( self.parent_path )
    else:
      parent = None
    n = self.model.insert( parent, self.position, self.new_row )
    self.view.expand_to_path( self.model[n].path )

  def redo(self):
    if self.deletion:
      self.delete()
    else:
      self.insert()

  def undo(self):
    if self.deletion:
      self.insert()
    else:
      self.delete()
