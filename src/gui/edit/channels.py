# vim: ts=2:sw=2:tw=80:nowrap
import gtk, gobject

from helpers import *
from ... import backend

ui_info = \
"""<ui>
  <popup name='CH:Edit'>
    <menuitem action='CH:Scaling'/>
    <separator/>
    <menuitem action='CH:Device'/>
  </popup>
</ui>"""


def edit_device(action, path, model, add_undo=None):
  print 'should edit the device settings (clock, trigger,...)'

def edit_scaling(action, path, model, ITEM, add_undo=None):
  #row[col] = do_script_edit(text=row[col])[1]
  print 'should edit the scaling...'

def create_action_group():
  # GtkActionEntry
  entries = (
    ( 'CH:Scaling', None,               # name, stock id
      'Scaling...', None,     # label, accelerator
      'Edit Scaling'),          # tooltip
    ( 'CH:Device', None,                # name, stock id
      'Device Settings', None,          # label, accelerator
      'Device Settings'),               # tooltip
  )

  # GtkToggleActionEntry
  toggle_entries = (
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





device_combobox_tree = gtk.TreeStore(str,str)

def build_device_combobox_tree():
  global device_combobox_tree
  T = device_combobox_tree
  T.clear()

  add_paths_to_combobox_tree( T, backend.analog,  'Analog',  skip_CAT=0 )
  add_paths_to_combobox_tree( T, backend.digital, 'Digital', skip_CAT=0 )



def load_devices_combobox( cell, editable, path ):
  global device_combobox_tree
  if len(device_combobox_tree) < 1:
    build_device_combobox_tree()
  editable.set_property("model", device_combobox_tree)
  prep_combobox_for_tree(editable)



def query_tooltip(widget, x, y, keyboard_tip, tooltip):
  try:
    channels, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    markup = ''
    sep = ''

    enable, scaling = channels.get(iter, channels.ENABLE, channels.SCALING)
    markup += \
      '<b>Scaling</b>:  {scaling}' \
      ''.format(**locals())

    tooltip.set_markup(markup)
    widget.set_tooltip_row(tooltip, path)
    return True
  except:
    return False






class Channels:
  def __init__(self, channels, add_undo=None):
    self.add_undo = add_undo
    self.channels = channels

    V = self.view = gtk.TreeView( channels )

    R = {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
      'scaling' : gtk.CellRendererText(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    }

    R['label'].set_property( 'editable', True )
    R['label'].connect( 'edited', set_item,
                        channels, channels.LABEL, self.add_undo, True )

    R['device'].set_property( 'editable', True )
    R['device'].set_property("text-column", 0)
    R['device'].connect( 'edited', set_item,
                         channels, channels.DEVICE, self.add_undo )
    R['device'].connect( 'editing-started', load_devices_combobox )

    R['value'].set_property( 'editable', True )
    R['value'].connect( 'edited', set_item,
                        channels, channels.VALUE, self.add_undo )

    R['scaling'].set_property( 'editable', True )
    R['scaling'].connect( 'edited', set_item,
                          channels, channels.SCALING, self.add_undo )

    R['enable'].set_property( 'activatable', True )
    R['enable'].connect( 'toggled', toggle_item,
                          channels, channels.ENABLE, self.add_undo )

    C = {
      'label'   : GTVC( 'Label',   R['label'],  text=channels.LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=channels.DEVICE ),
      'scaling' : GTVC( 'Scaling', R['scaling'],text=channels.SCALING ),
      'value'   : GTVC( 'Value',   R['value'],  text=channels.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    }

    C['enable'].add_attribute( R['enable'], 'active', channels.ENABLE )

    #V.set_property( 'hover_selection', True )
    V.set_property( 'has_tooltip', True )
    V.connect('query-tooltip', query_tooltip)
    V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
    V.append_column( C['label'  ] )
    #V.append_column( C['scaling'] )
    V.append_column( C['value'  ] )
    V.append_column( C['enable' ] )
    V.append_column( C['device' ] )

    ui_manager = mkUIManager()
    V.connect('button-press-event',
      popup_button_press_handler,
      ui_manager,
      ui_manager.get_widget('/CH:Edit'),
      [('/CH:Edit/CH:Scaling', edit_scaling, channels.SCALING, self.add_undo),
       ('/CH:Edit/CH:Device',  edit_device,                    self.add_undo)],
    )


  def insert_row(self):
    i = self.channels.insert_before(self.view.get_selection().get_selected()[1])
    self.add_undo( ListUndo(i, self.channels) )

  def delete_row(self):
    i = self.view.get_selection().get_selected()[1]
    if i:
      n = self.channels.iter_next( i )
      self.add_undo( ListUndo(i, self.channels, deletion=True) )
      self.channels.remove( i )
      if n:
        self.view.get_selection().select_iter( n )


class ListUndo:
  def __init__(self, iter, model, deletion=False):
    self.model = model
    self.path = model.get_path( iter )
    self.position = self.path[0]
    self.new_row = list(model[iter])
    self.deletion = deletion

  def delete(self):
    self.model.remove( self.model.get_iter(self.path) )

  def insert(self):
    self.model.insert( self.position, self.new_row )

  def redo(self):
    if self.deletion: self.delete()
    else:             self.insert()

  def undo(self):
    if self.deletion: self.insert()
    else:             self.delete()
