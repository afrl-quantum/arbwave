# vim: ts=2:sw=2:tw=80:nowrap
import gtk, gobject

from helpers import *
import scaling
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

  add_paths_to_combobox_tree(
    T, backend.get_analog_channels(),  'Analog',  skip_CAT=0 )
  add_paths_to_combobox_tree(
    T, backend.get_digital_channels(), 'Digital', skip_CAT=0 )



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

    enable, units, scaling, order, smooth = channels.get(iter,
      channels.ENABLE,
      channels.UNITS,
      channels.SCALING,
      channels.INTERP_ORDER,
      channels.INTERP_SMOOTHING)
    markup += \
      '<b>Dimensions</b>:  {units}' \
      .format(**locals())
    if scaling and len(scaling):
      markup += \
      '\n<b>UnivariateSpline(x,y,order,smooth)</b>:\n' \
      '\torder  : {order}\n' \
      '\tsmooth : {smooth}\n' \
      '\t(x,y)  :\n' \
      .format(**locals())
      for r in scaling:
        markup += '\t\t{x}\t{y}\n'.format(x=r[0], y=r[1])

    tooltip.set_markup(markup)
    widget.set_tooltip_row(tooltip, path)
    return True
  except:
    return False






class Channels:
  def __init__(self, channels, processor, parent=None, add_undo=None):
    self.parent = parent
    self.add_undo = add_undo
    self.channels = channels
    self.processor = processor
    self.scaling_editor = None

    V = self.view = gtk.TreeView( channels )

    R = {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
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

    R['enable'].set_property( 'activatable', True )
    R['enable'].connect( 'toggled', toggle_item,
                          channels, channels.ENABLE, self.add_undo )

    C = {
      'label'   : GTVC( 'Label',   R['label'],  text=channels.LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=channels.DEVICE ),
      'value'   : GTVC( 'Value',   R['value'],  text=channels.VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'] ),
    }

    C['enable'].add_attribute( R['enable'], 'active', channels.ENABLE )

    #V.set_property( 'hover_selection', True )
    V.set_property( 'has_tooltip', True )
    V.connect('query-tooltip', query_tooltip)
    V.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), V)
    V.append_column( C['label'  ] )
    V.append_column( C['value'  ] )
    V.append_column( C['enable' ] )
    V.append_column( C['device' ] )

    ui_manager = mkUIManager()
    V.connect('button-press-event',
      popup_button_press_handler,
      ui_manager,
      ui_manager.get_widget('/CH:Edit'),
      [('/CH:Edit/CH:Scaling', self.edit_scaling),
       ('/CH:Edit/CH:Device',  edit_device, self.add_undo)],
    )


  def edit_scaling(self, action, path, model):
    def unset_editor(*args):
      self.scaling_editor = None

    if not self.scaling_editor:
      self.scaling_editor = scaling.Editor(
        channels=self.channels,
        parent=self.parent,
        globals_src=lambda: self.processor.get_globals(),
        add_undo=self.add_undo,
      )
      self.scaling_editor.connect('destroy', unset_editor)
      self.scaling_editor.set_channel(model[path][model.LABEL])
    self.scaling_editor.present()


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
