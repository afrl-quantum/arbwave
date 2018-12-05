# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk, Gdk as gdk, GObject as gobject
import logging

from .helpers import *
from .script import edit as do_script_edit
import threading
from . import waveformsset

from ...tools.gui_callbacks import do_gui_operation

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
  except gobject.GError as msg:
    print('building popup menu failed:', msg)
  return merge

def is_group( model, path ):
  # the '| 0x2' is so that we can get the waveform selector shown in any case
  return model.iter_has_child( model.get_iter(path) )

def load_channels_combobox( cell, editable, path, model, channels ):
  chls = gtk.ListStore(str)
  editable.set_property("model", chls)
  chls.append(('',)) # add a blank line to allow selection of 'empty' channel

  if callable(model): # allow for a callback to be used to get model
    model = model()
  # ensure that group-level items edit text and do not use drop down
  child = editable.get_child()
  if not( is_group(model, path) and type(child) is gtk.Entry ):
    child.set_property('editable', False)
    for i in iter(channels):
      chls.append([ i[channels.LABEL] ])

def allow_value_edit( cell, editable, path, model ):
  """Ensure that group-level items cannot edit value"""
  if callable(model): # allow for a callback to be used to get model
    model = model()
  assert type(editable) is gtk.Entry, 'value type is not gtk.Entry(?)!'
  if is_group( model, path ):
    editable.set_property('editable', False)




def begin_drag(w, ctx, parent):
  # pause updates because of waveform updates
  parent.pause()

def drag_motion(w, ctx, x, y, time, parent):
  mask = w.get_window().get_pointer()[2]
  if mask & gdk.ModifierType.CONTROL_MASK:
    gdk.drag_status( ctx, gdk.DragAction.COPY, time )

def end_drag(w, ctx, parent, wf):
  # unpause updates and force an update based on waveform changes
  if callable(wf):
    wf = wf()
  parent.unpause()
  parent.update(wf)


def gather_paths(channels, wvfms, i):
  L = list()
  dev = None
  for c in iter(channels):
    if wvfms[i][wvfms.CHANNEL] == c[channels.LABEL]:
      dev = c[channels.DEVICE]
  if dev:
    # Gtk3 returns path as object type, we need it still as a tuple of indices
    # for the cache lookup (and sorting the cache)...
    L.append( (tuple(wvfms.get_path(i).get_indices()), dev.partition('/')[-1]) )
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
    do_gui_operation(plotter.highlight_parts, paths)
  else:
    do_gui_operation(plotter.highlight_parts, list())


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
    self.waveforms.connect_wf_change( self.set_waveform )
    self.parent = parent

    waveform = self.get_waveform()

    V = self.view = gtk.TreeView( waveform )
    V.set_reorderable(True)
    V.connect('drag-begin', begin_drag, parent)
    V.connect('drag-end', end_drag, parent, self.get_waveform)
    V.connect('drag-motion', drag_motion, parent)
    V.get_selection().connect('changed',highlight,self.parent.plotter,channels)
    V.connect('key-press-event', clear_selection)

    R = {
      'channel' : gtk.CellRendererCombo(),
      'time'    : GCRT(),
      'duration': GCRT(),
      'value'   : GCRT(),
      'enable'  : gtk.CellRendererToggle(),
    }

    R['channel'].set_property( 'editable', True )
    R['channel'].set_property('text-column', 0)
    R['channel'].set_property('has-entry', True)
    R['channel'].connect( 'edited', set_item,
                          self.get_waveform, waveform.CHANNEL, self.add_undo )
    R['channel'].connect( 'editing-started', load_channels_combobox,
                          self.get_waveform, channels )

    R['time'].set_property( 'editable', True )
    R['time'].connect( 'edited', set_item,
                       self.get_waveform, waveform.TIME, self.add_undo )

    R['duration'].set_property( 'editable', True )
    R['duration'].connect( 'edited', set_item,
                           self.get_waveform, waveform.DURATION, self.add_undo )

    R['value'].set_property( 'editable', True )
    R['value'].connect( 'edited', set_item,
                        self.get_waveform, waveform.VALUE, self.add_undo )
    R['value'].connect( 'editing-started', allow_value_edit, self.get_waveform)

    R['enable'].set_property( 'activatable', True )
    R['enable'].connect( 'toggled', toggle_item,
                         self.get_waveform, waveform.ENABLE, self.add_undo )

    C = {
      'channel' : GTVC( 'Channel', R['channel'], text=waveform.CHANNEL ),
      'time'    : GTVC( 'Time',    R['time'],    text=waveform.TIME ),
      'duration': GTVC( 'Duration',R['duration'],text=waveform.DURATION ),
      'value'   : GTVC( 'Value',   R['value'],   text=waveform.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    }

    C['enable'].add_attribute( R['enable'], 'active', waveform.ENABLE )

    V.set_property( 'hover_selection', True )
    V.set_property( 'has_tooltip', True )
    V.connect('query-tooltip', self.query_tooltip)
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
      [('/WFG:Edit/WFG:Async', toggle_item,  waveform.ASYNC,  self.add_undo),
       ('/WFG:Edit/WFG:Script', edit_script, waveform.SCRIPT, self.add_undo)],
      self.add_waveform_select_menu,
      True,
    )

    self.eval_cache_lock = threading.Lock()
    self.eval_cache = dict()


  def add_waveform_select_menu(self, popup, not_group):
    WF_LABEL = 'Waveforms'
    # clean up from last time if necessary
    if popup.get_children()[-1].get_label() == WF_LABEL:
      m = popup.get_children()[-1]
      sep0 = popup.get_children()[-2]
      sep1 = popup.get_children()[-3]
      popup.remove(m)
      popup.remove(sep0)
      popup.remove(sep1)
      sub = m.get_submenu()
      for c in sub.get_children():
        sub.remove( c )
        del c
      m.set_submenu(None)
      del sub, m, sep0, sep1

    header = gtk.MenuItem('Select Waveform:')
    header.set_sensitive(False)

    submenu = gtk.Menu()
    submenu.append(header)
    submenu.append( gtk.SeparatorMenuItem() )

    # now add all the known waveforms
    r = None
    curr = self.waveforms.get_current()
    for l in self.waveforms.wf_dict().keys():
      r = gtk.RadioMenuItem(group=r, label=l)
      if l == curr:
        r.activate()
      r.connect('toggled', self.select_waveform)
      submenu.append( r )

    # now add pointer to editor
    submenu.append( gtk.SeparatorMenuItem() )
    submenu.append( gtk.SeparatorMenuItem() )
    me = gtk.MenuItem('Edit')
    me.connect('activate', self.edit_waveform_list)
    submenu.append( me )

    # add to main menu
    wm = gtk.MenuItem(WF_LABEL)
    wm.set_submenu(submenu)
    wm.show_all()
    popup.append( gtk.SeparatorMenuItem() )
    popup.append( gtk.SeparatorMenuItem() )
    popup.append( wm )
    if not_group:
      popup.show_all()
    else:
      for c in popup.get_children()[:-1]:
        c.hide()


  def select_waveform(self, item):
    wf = item.get_label()
    if wf == self.waveforms.get_current() or not item.get_active():
      return
    self.parent.pause()
    if wf != self.waveforms.get_current():
      self.waveforms.set_current(wf)
      # re-enable updates and directly call for an update
      self.parent.unpause()
      self.parent.update(self.get_waveform())
    self.parent.unpause()


  def edit_waveform_list(self,*args):
    D = waveformsset.Dialog(self.waveforms, parent=self.parent)
    D.show()


  def get_waveform(self):
    return self.waveforms.get_wf()


  def set_waveform(self, label):
    WFD = self.waveforms.wf_dict()
    assert label in WFD, 'Cannot select unknown waveform!'
    def set():
      logging.debug('reset waveform_editor.view.model..........')
      self.view.set_model( WFD[label] )
      logging.debug('reset waveform_editor.view.model finished.')
    do_gui_operation( set )


  def set_eval_cache(self, cache):
    try:
      self.eval_cache_lock.acquire()
      self.eval_cache = cache
    finally:
      self.eval_cache_lock.release()

  def get_eval_cache(self):
    try:
      self.eval_cache_lock.acquire()
      return self.eval_cache
    finally:
      self.eval_cache_lock.release()

  def query_tooltip(self, widget, x, y, keyboard_tip, tooltip):
    is_row, x, y, waveform, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    if not is_row:
      return False

    # Gtk3 returns path as object type, we need it still as a tuple of indices
    # for the cache lookup (and sorting the cache)...
    path_tuple = tuple(path.get_indices())

    markup = ''
    sep = ''
    script, async_ = waveform.get(iter, waveform.SCRIPT, waveform.ASYNC)

    if is_group( waveform, path ): # group-only information
      if async_ is not None:
        desc = {
          True : 'will <u><b>not</b></u>',
          False: '<b>will</b>',
        }
        markup += sep + \
          '<b>Asynchronous:</b>  {a}\n' \
          '    Group {d} be used for calculation of \n' \
          "    natural time 't' for subsequent waveform groups" \
          ''.format(a=async_,d=desc[async_])
        sep = '\n'
      if script:
        markup += sep + \
          '<b>Script:</b>\n' \
          '<span size="small">{s}</span>' \
          .format(s=script)
        sep = '\n'

    cache = self.get_eval_cache()
    if path_tuple in cache:
      C = cache[path_tuple]
      tf = C['t'] + C['dt']
      tf.fmt = C['t'].fmt = C['dt'].fmt = '{coeff} {units}'
      markup += sep + \
        '<b>time:</b>\n' \
        '  {t} -&gt; {tf}  (dt = {dt})' \
        .format(tf=tf, **C)
      if 'val' in C:
        markup += '\n<b>value:</b>  {}' \
          .format( C['val'].replace('<', '&lt;').replace('>', '&gt;') )
      sep = '\n'

    tooltip.set_markup( markup )
    widget.set_tooltip_row(tooltip, path)
    return True




  def insert_waveform(self):
    self.parent.pause()
    waveform = self.get_waveform()
    i = self.view.get_selection().get_selected()[1]
    if not i: # append new element to last group
      n = waveform.append( None, waveform.default_element )
    else: # insert into group before selected item
      iter = waveform[i].iter
      p = waveform[i].parent
      if p: pi = p.iter
      else: pi = None
      n = waveform.insert_before(pi, iter, waveform.default_element)
    self.view.expand_to_path( waveform[n].path )

    self.add_undo( TreeUndo(n, waveform, self.view) )
    self.parent.unpause()
    self.parent.update(waveform)



  def delete_row(self):
    waveform = self.get_waveform()
    i = self.view.get_selection().get_selected()[1]
    if i:
      n = waveform.iter_next( i )
      self.add_undo( TreeUndo(i, waveform, self.view, deletion=True) )
      waveform.remove( i )
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
