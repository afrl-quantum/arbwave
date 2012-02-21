# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gtk, gobject

import sys

# local packages
import about
from packing import Args, hpack, VBox
import plotter
import tmpconfig


def load_channels_combobox( cell, editable, path, channels ):
  chls = gtk.ListStore(int,str)
  for i in xrange( len(channels) ):
    chls.append( [i, str(i) + ': ' + channels[i][0]] )

  editable.set_property("model", chls)

def load_devices_combobox( cell, editable, path ):
  devls = gtk.ListStore(str)
  for i in tmpconfig.devs:
    devls.append( [i] )

  editable.set_property("model", devls)

def create_channel_list_store():
  return gtk.ListStore( gobject.TYPE_STRING, # Label
                        gobject.TYPE_STRING, # device
                        gobject.TYPE_STRING, # value
                        gobject.TYPE_BOOLEAN ) #enabled

def create_waveform_tree_store():
  return gtk.TreeStore( gobject.TYPE_STRING, # channel
                        gobject.TYPE_STRING, # Time
                        gobject.TYPE_STRING, # value
                        gobject.TYPE_BOOLEAN ) #enabled

def load_waveform_tree_store(tree_store, config):
  # places the global people data into the list
  # we form a simple tree.
  for item in config.keys():
    parent = tree_store.append(
      None,
      (item, None, None, True)
    )
    for task in config[item]:
      tree_store.append(
          parent,
          (task[0], task[1], task[2], True)
      )

def set_item( cell, path, new_item, waveforms, ITEM ):
  waveforms[path][ITEM] = new_item

def toggle_item( cell, path, waveforms, ITEM ):
  """
  Sets the toggled state on the toggle button to true or false.
  """
  model[path][ITEM] = not model[path][ITEM]

def GTVC(*args,**kwargs):
  c = gtk.TreeViewColumn(*args,**kwargs)
  c.set_property('resizable', True)
  return c

def create_channel_editor():
  LABEL   =0
  DEVICE  =1
  VALUE   =2
  ENABLE  =3

  channels = create_channel_list_store()
  channel_editor = {
    'view'      : gtk.TreeView( channels ),
    'renderers' : {
      'label'   : gtk.CellRendererText(),
      'device'  : gtk.CellRendererCombo(),
      'value'   : gtk.CellRendererText(),
      'enable'  : gtk.CellRendererToggle(),
    },
  }
  R = channel_editor['renderers']
  channel_editor.update({
    'columns' : {
      'label'   : GTVC( 'Label',   R['label'],    text=LABEL ),
      'device'  : GTVC( 'Device',  R['device'], text=DEVICE ),
      'value'   : GTVC( 'Value',   R['value'],  text=VALUE ),
      'enable'  : GTVC( 'Enabled', R['enable'], text=ENABLE ),
    },
  })

  R['label'].set_property( 'editable', True )
  R['label'].connect( 'edited', set_item, channels, LABEL )

  R['device'].set_property( 'editable', True )
  R['device'].set_property("text-column", 1)
  R['device'].connect( 'edited', set_item, channels, DEVICE )
  R['device'].connect( 'editing-started', load_devices_combobox )

  R['value'].set_property( 'editable', True )
  R['value'].connect( 'edited', set_item, channels, VALUE )

  R['enable'].set_property( 'activatable', True )
  R['enable'].connect( 'toggled', toggle_item, channels, ENABLE )

  C = channel_editor['columns']
  V = channel_editor['view']
  C['enable'].add_attribute( R['enable'], 'active', ENABLE )
  V.set_property( 'hover_selection', True )
  V.append_column( C['label'] )
  V.append_column( C['device'] )
  V.append_column( C['value'] )
  V.append_column( C['enable'] )
  return channels, channel_editor

def create_waveform_editor(channels):
  CHANNEL =0
  TIME    =1
  VALUE   =2
  ENABLE  =3

  waveforms = create_waveform_tree_store()
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

  return waveforms, waveform_editor




ui_info = \
'''<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='New'/>
      <menuitem action='Open'/>
      <menuitem action='Save'/>
      <menuitem action='SaveAs'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='EditMenu'>
      <!-- 
      <menuitem action='Cut'/>
      <menuitem action='Copy'/>
      <menuitem action='Paste'/>
      <separator/>
      -->
      <menuitem action='Configure'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
    </menu>
  </menubar>
  <toolbar  name='ToolBar'>
    <toolitem action='New'/>
    <toolitem action='Open'/>
    <toolitem action='Save'/>
    <separator/>
    <toolitem action='Configure'/>
    <separator/>
    <toolitem action='Run'/>
  </toolbar>
</ui>'''

VERSION = 'arbwave-0.0.1'

class ArbWave(gtk.Window):
  def __init__(self, parent=None):
    #create the toplevel window
    gtk.Window.__init__(self)
    self.set_title('Arbitrary Waveform Generator')
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      self.connect('destroy', lambda *w: gtk.main_quit())

    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
        mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
        print "building menus failed: %s" % msg

    #  ###### SET UP THE PANEL #######
    self.channels, self.channel_editor = create_channel_editor()
    self.waveforms, self.waveform_editor = create_waveform_editor(self.channels)
    self.axes, self.fig, self.canvas, self.toolbar = plotter.create(self)

    chlabel = gtk.Label('Channels')
    chlabel.set_property('angle', 90)
    self.channel_editor['view'].set_size_request( 100, 200 )
    chbox = gtk.EventBox()
    chbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16962,36237,65535))
    chbox.add(hpack( Args(chlabel,False), self.channel_editor['view']))

    wlabel = gtk.Label('Waveforms')
    wlabel.set_property('angle', 90)
    self.waveform_editor['view'].set_size_request( -1, 200 )
    wbox = gtk.EventBox()
    wbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16962,36237,65535))
    wbox.add(hpack( Args(wlabel,False), self.waveform_editor['view']))

    self.canvas.set_size_request( 800, 200 )
    #self.canvas_scroll = gtk.HScale()

    vbox = VBox()
    self.add(vbox)
    vbox.pack_start( merge.get_widget('/MenuBar'), False, False, 0 )
    vbox.pack_start( hpack( merge.get_widget('/ToolBar'), gtk.VSeparator(), self.toolbar ), False )
    top = gtk.HPaned()
    top.pack1( chbox, True, False )
    top.pack2( wbox, True, False )
    bottom = VBox()
    bottom.pack_start( self.canvas )
    #bottom.pack_start( self.canvas_scroll, False, False )

    body = gtk.VPaned()
    body.pack1( top, True )
    body.pack2( bottom, True )
    vbox.pack_start( body )

    self.show_all()


  def create_action_group(self):
    # GtkActionEntry
    entries = (
      ( 'FileMenu', None, '_File' ),               # name, stock id, label
      ( 'EditMenu', None, '_Edit' ),               # name, stock id, label
      ( 'HelpMenu', None, '_Help' ),               # name, stock id, label
      ( 'New', gtk.STOCK_NEW,                      # name, stock id
        '_New', '<control>N',                      # label, accelerator
        'Create a new file',                       # tooltip
        self.activate_action ),
      ( 'Open', gtk.STOCK_OPEN,                    # name, stock id
        '_Open','<control>O',                      # label, accelerator
        'Open a file',                             # tooltip
        self.activate_action ),
      ( 'Save', gtk.STOCK_SAVE,                    # name, stock id
        '_Save','<control>S',                      # label, accelerator
        'Save current file',                       # tooltip
        self.activate_action ),
      ( 'SaveAs', gtk.STOCK_SAVE_AS,               # name, stock id
        'Save _As...', '<shift><control>S',        # label, accelerator
        'Save to a file',                          # tooltip
        self.activate_action ),
      ( 'Quit', gtk.STOCK_QUIT,                    # name, stock id
        '_Quit', '<control>Q',                     # label, accelerator
        'Quit',                                    # tooltip
        self.activate_action ),
      # ( 'Cut', gtk.STOCK_CUT,                      # name, stock id
      #   '_Cut', '<control>X',                      # label, accelerator
      #   'Cut text',                                # tooltip
      #   self.activate_action ),
      # ( 'Copy', gtk.STOCK_COPY,                    # name, stock id
      #   '_Copy', '<control>C',                     # label, accelerator
      #   'Copy text',                               # tooltip
      #   self.activate_action ),
      # ( 'Paste', gtk.STOCK_PASTE,                  # name, stock id
      #   '_Paste', '<control>V',                    # label, accelerator
      #   'Paste text',                              # tooltip
      #   self.activate_action ),
      ( 'Configure', gtk.STOCK_PREFERENCES,        # name, stock id
        '_Configure', None,                        # label, accelerator
        'Configure triggers, backplane, etc.',     # tooltip
        self.activate_action ),
      ( 'About', None,                             # name, stock id
        '_About', '<control>A',                    # label, accelerator
        'About',                                   # tooltip
        self.activate_action ),
    )

    # GtkToggleActionEntry
    toggle_entries = (
      ( 'Run', gtk.STOCK_MEDIA_PLAY,               # name, stock id
         '_Run', '<control>space',                 # label, accelerator
        'Activate waveform output',                # tooltip
        self.activate_action,
        True ),                                    # is_active
    )

    #     # Create the menubar and toolbar
    action_group = gtk.ActionGroup('ArbWaveGUIActions')
    action_group.add_actions(entries)
    action_group.add_toggle_actions(toggle_entries)

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'Quit'      : lambda: self.destroy(),
      'Configure' : lambda: sys.stderr.write('configuring...\n'),
      'Run'       : lambda: sys.stderr.write('running...\n'),
      'About'     : lambda: about.show(),
    }

    return action_group

  def activate_action(self, action):
    if action.get_name() not in self.actions:
      raise LookupError(
        'Could not find application action: "'+action.get_name()+'"'
      )
    self.actions[action.get_name()]()

