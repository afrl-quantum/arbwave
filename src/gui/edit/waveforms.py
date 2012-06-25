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


class Waveforms:
  def __init__(self, waveforms, channels, parent, add_undo=None):
    self.add_undo = add_undo
    self.waveforms = waveforms

    V = self.view = gtk.TreeView( waveforms )
    V.set_reorderable(True)
    V.connect('drag-begin', begin_drag, parent)
    V.connect('drag-end', end_drag, parent, waveforms)
    V.connect('drag-motion', drag_motion, parent)

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

    #V.set_property( 'hover_selection', True )
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
      ui_manager,
      ui_manager.get_widget('/WFG:Edit'),
      [('/WFG:Edit/WFG:Async', toggle_item,  waveforms.ASYNC,  self.add_undo),
       ('/WFG:Edit/WFG:Script', edit_script, waveforms.SCRIPT, self.add_undo)],
    )



  def insert_waveform_group(self):
    i = self.view.get_selection().get_selected()[1]
    if not i: # append new grouping to end
      n = self.waveforms.append( None, self.waveforms.default_group )
    elif self.waveforms[i].parent:
      n = self.waveforms.insert_before(
        None, self.waveforms[i].parent.iter,
        self.waveforms.default_group )
    else:
      n = self.waveforms.insert_before( None, i, self.waveforms.default_group )
    self.add_undo( TreeUndo(n, self.waveforms, self.view) )


  def insert_waveform(self):
    p = None
    i = self.view.get_selection().get_selected()[1]
    if not i: # append new element to last group
      if len( self.waveforms ) == 0:
        # create last if necessary
        p = self.waveforms.append( None, self.waveforms.default_group )
      n = self.waveforms.append( self.waveforms[-1].iter, \
                                 self.waveforms.default_element )
    elif not self.waveforms[i].parent: #append to selected group
      n = self.waveforms.append( i, self.waveforms.default_element )
    else: # insert into group before selected item
      n = self.waveforms.insert_before(
        self.waveforms[i].parent.iter, i,
        self.waveforms.default_element )
    self.view.expand_to_path( self.waveforms[n].path )

    self.add_undo( TreeUndo(n, self.waveforms, self.view, new_parent=p) )



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
  def __init__(self, iter, model, view, deletion=False, new_parent=None):
    self.model = model
    self.view = view
    self.path = model.get_path( iter )
    self.position = self.path[-1]
    self.parent_path = self.path[:-1]
    self.new_row = list(model[iter])
    self.deletion = deletion
    self.parent_undo = NullUndo()
    if new_parent:
      self.parent_undo = TreeUndo( new_parent, model, view, deletion )

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
      self.parent_undo.redo()
    else:
      self.parent_undo.redo()
      self.insert()

  def undo(self):
    if self.deletion:
      self.parent_undo.undo()
      self.insert()
    else:
      self.delete()
      self.parent_undo.undo()
