# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gtk, gobject

import sys

# local packages
import about, configure, plotter, stores, edit
from packing import Args as PArgs, hpack, vpack, VBox
import storage

from .. import backend



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
      <menuitem action='Script'/>
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
    <toolitem action='Script'/>
    <separator/>
    <toolitem action='Run'/>
  </toolbar>
  <toolbar  name='ChannelToolBar'>
    <toolitem action='CH:Add'/>
    <toolitem action='CH:Delete'/>
    <separator/>
    <toolitem action='CH:Up'/>
    <toolitem action='CH:Down'/>
  </toolbar>
  <toolbar  name='WaveformToolBar'>
    <toolitem action='WF:Add:group'/>
    <toolitem action='WF:Add'/>
    <toolitem action='WF:Delete'/>
    <separator/>
    <toolitem action='WF:Up'/>
    <toolitem action='WF:Down'/>
  </toolbar>
</ui>'''

default_script = """\
# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.

def onstart():
	'''Called when 'play' button is clicked'''
	pass

def onstop():
	'''Called when 'stop' button is clicked.'''
	pass

import arbwave
def loop_control(*args, **kwargs):
	for i in [1,2,3]:
		for j in [1,2,3]:
			arbwave.update()

arbwave.connect( 'start', onstart )
arbwave.connect( 'stop', onstop )
#arbwave.set_loop_control( loop_control )
"""

class ArbWave(gtk.Window):
  def __init__(self, parent=None):
    #create the toplevel window
    gtk.Window.__init__(self)
    self.set_title('Arbitrary Waveform Generator')
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      self.connect('destroy', lambda *w: gtk.main_quit())


    # LOAD THE STORAGE
    self.script = stores.Script(
      default_script,
      title='Global Variables/Functions...',
      parent=self,
      changed=self.update,
    )
    self.channels = stores.Channels( changed=self.update )
    self.waveforms = stores.Waveforms( changed=self.update )
    self.signals = stores.Signals( changed=self.update )
    self.channel_editor  = edit.channels.create(self.channels)
    self.waveform_editor = edit.waveforms.create(self.waveforms, self.channels)
    self.plotter = plotter.create(self)
    self.allow_updates = True


    #  ###### SET UP THE PANEL #######
    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      print 'building menus failed: {msg}'.format(msg=msg)

    chlabel = gtk.Label('Channels')
    chlabel.set_property('angle', 90)
    chtools = merge.get_widget('/ChannelToolBar')
    chtools.set_property('orientation', gtk.ORIENTATION_VERTICAL )
    chtools.set_property('icon-size', gtk.ICON_SIZE_MENU)
    chtools.set_property('toolbar-style', gtk.TOOLBAR_ICONS)
    chew = gtk.ScrolledWindow()
    chew.set_size_request( -1, -1 )
    chew.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    chew.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    chew.add( self.channel_editor['view'] )
    chbox = gtk.EventBox()
    chbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16962,36237,65535))
    chbox.add(
      hpack(
        PArgs( vpack(chtools, PArgs(chlabel,False)), False),
        chew,
      )
    )


    wlabel = gtk.Label('Waveforms')
    wlabel.set_property('angle', 90)
    wtools = merge.get_widget('/WaveformToolBar')
    wtools.set_property('orientation', gtk.ORIENTATION_VERTICAL )
    wtools.set_property('icon-size', gtk.ICON_SIZE_MENU)
    wtools.set_property('toolbar-style', gtk.TOOLBAR_ICONS)
    wew = gtk.ScrolledWindow()
    wew.set_size_request(-1,225)
    wew.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    wew.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    wew.add( self.waveform_editor['view'] )
    wbox = gtk.EventBox()
    wbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16962,36237,65535))
    wbox.add(
      hpack(
        PArgs( vpack(wtools, PArgs(wlabel,False)), False),
        wew,
      )
    )


    self.plotter['canvas'].set_size_request( 800, 200 )
    #self.canvas_scroll = gtk.HScale()

    top = gtk.HPaned()
    top.pack1( chbox, True, False )
    top.pack2( wbox, True, False )
    bottom = VBox()
    bottom.pack_start( self.plotter['canvas'] )
    #bottom.pack_start( self.canvas_scroll, False, False )

    body = gtk.VPaned()
    body.pack1( top, True )
    body.pack2( bottom, True )

    self.add( vpack(
        PArgs( merge.get_widget('/MenuBar'), False, False, 0 ),
        PArgs( # MENU BAR LOCATION
          hpack( merge.get_widget('/ToolBar'),
                 PArgs(gtk.VSeparator(), False),
                 PArgs(gtk.VSeparator(), False),
                 self.plotter['toolbar'],
          ), False ),
        body
    ))

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
        '_Configure Devices', None,                # label, accelerator
        'Configure triggers, backplane, etc.',     # tooltip
        self.activate_action ),
      ( 'Script', gtk.STOCK_EDIT,                  # name, stock id
        'Edit Global _Script', None,               # label, accelerator
        'Set global variables, define global functions...',# tooltip
        self.activate_action ),
      ( 'About', None,                             # name, stock id
        '_About', '<control>A',                    # label, accelerator
        'About',                                   # tooltip
        self.activate_action ),

      # CHANNEL EDITOR
      ( 'CH:Add', gtk.STOCK_ADD,                   # name, stock id
        None, None,                                # label, accelerator
        'Add channel after current channel',       # tooltip
        self.activate_action ),
      ( 'CH:Delete', gtk.STOCK_DELETE,             # name, stock id
        None, None,                                # label, accelerator
        'Delete current channel',                  # tooltip
        self.activate_action ),
      ( 'CH:Up', gtk.STOCK_GO_UP,                  # name, stock id
        None, None,                                # label, accelerator
        'Move current channel up',                 # tooltip
        self.activate_action ),
      ( 'CH:Down', gtk.STOCK_GO_DOWN,              # name, stock id
        None, None,                                # label, accelerator
        'Move current channel up',                 # tooltip
        self.activate_action ),

      # WAVEFORM EDITOR
      ( 'WF:Add:group', gtk.STOCK_NEW,             # name, stock id
        None, None,                                # label, accelerator
        'Add waveform group after '
        'current waveform group',                  # tooltip
        self.activate_action ),
      ( 'WF:Add', gtk.STOCK_ADD,                   # name, stock id
        None, None,                                # label, accelerator
        'Add waveform element after '
        'current waveform element',                # tooltip
        self.activate_action ),
      ( 'WF:Delete', gtk.STOCK_DELETE,             # name, stock id
        None, None,                                # label, accelerator
        'Delete current waveform element',         # tooltip
        self.activate_action ),
      ( 'WF:Up', gtk.STOCK_GO_UP,                  # name, stock id
        None, None,                                # label, accelerator
        'Move current waveform element up',        # tooltip
        self.activate_action ),
      ( 'WF:Down', gtk.STOCK_GO_DOWN,              # name, stock id
        None, None,                                # label, accelerator
        'Move current waveform element up',        # tooltip
        self.activate_action ),
    )

    # GtkToggleActionEntry
    toggle_entries = (
      ( 'Run', gtk.STOCK_MEDIA_PLAY,               # name, stock id
         '_Run', '<control>space',                 # label, accelerator
        'Activate waveform output',                # tooltip
        self.activate_action,
        False ),                                    # is_active
    )

    def switch_play_stop_icons(action):
      if action.get_property('stock-id') == gtk.STOCK_MEDIA_PLAY:
        action.set_property('stock-id', gtk.STOCK_MEDIA_STOP)
      else:
        action.set_property('stock-id', gtk.STOCK_MEDIA_PLAY)

    def add_waveform_group(action):
      i = self.waveform_editor['view'].get_selection().get_selected()[1]
      if not i: # append new grouping to end
        self.waveforms.append( None )
      elif self.waveforms[i].parent:
        self.waveforms.insert_before( None, self.waveforms[i].parent.iter )
      else:
        self.waveforms.insert_before( None, i )

    def add_waveform(action):
      i = self.waveform_editor['view'].get_selection().get_selected()[1]
      if not i: # append new element to last group
        if len( self.waveforms ) == 0:
          self.waveforms.append( None ) # create last if necessary
        n = self.waveforms.append( self.waveforms[-1].iter )
      elif not self.waveforms[i].parent:
        n = self.waveforms.append( i )
      else:
        n = self.waveforms.insert_before( self.waveforms[i].parent.iter, i )
      self.waveform_editor['view'].expand_to_path( self.waveforms[n].path )

    def delrow( action, stor, ed ):
      i = ed.get_selection().get_selected()[1]
      if i:
        n = stor.iter_next( i )
        stor.remove( i )
        if n:
          ed.get_selection().select_iter( n )

    def addrow( action, stor, ed ):
      stor.insert_before( ed.get_selection().get_selected()[1] )


    #     # Create the menubar and toolbar
    action_group = gtk.ActionGroup('ArbWaveGUIActions')
    action_group.add_actions(entries)
    action_group.add_toggle_actions(toggle_entries)

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'New'       : lambda a: self.clearvars(),
      'Open'      : ( storage.gtk_tools.gtk_open_handler, self ),
      'Save'      : ( storage.gtk_tools.gtk_save_handler, self ),
      'SaveAs'    : ( storage.gtk_tools.gtk_save_handler, self, True),
      'Quit'      : lambda a: self.destroy(),
      'Configure' : lambda a: configure.show(self, self),
      'Script'    : lambda a: self.script.edit(),
      'Run'       : switch_play_stop_icons,
      'About'     : lambda a: about.show(),
      'CH:Add'    : ( addrow, self.channels, self.channel_editor['view'] ),
      'CH:Delete' : ( delrow, self.channels, self.channel_editor['view'] ),
      'CH:Up'     : lambda a: sys.stderr.write('Move channel up\n'),
      'CH:Down'   : lambda a: sys.stderr.write('Move channel down\n'),
      'WF:Add:group': add_waveform_group,
      'WF:Add'    : add_waveform,
      'WF:Delete' : ( delrow, self.waveforms, self.waveform_editor['view'] ),
      'WF:Up'     : lambda a: sys.stderr.write('Move waveform element up\n'),
      'WF:Down'   : lambda a: sys.stderr.write('Move waveform element down\n'),
    }

    return action_group

  def activate_action(self, action):
    if action.get_name() not in self.actions:
      raise LookupError(
        'Could not find application action: "'+action.get_name()+'"'
      )
    A = self.actions[action.get_name()]
    if type(A) in [ tuple, list ]:
      A[0](action, *A[1:])
    else:
      A(action)


  def getvars(self):
    return {
      'global_script': self.script.representation(),
      'channels'  : self.channels.representation(),
      'waveforms' : self.waveforms.representation(),
      'signals'   : self.signals.representation(),
    }

  def setvars(self, vardict):
    # suspend all updates
    self.allow_updates = False

    if 'channels' in vardict:
      self.channels.load( vardict['channels'] )

    if 'waveforms' in vardict:
      self.waveforms.load( vardict['waveforms'] )

    if 'signals' in vardict:
      self.signals.load( vardict['signals'] )

    if 'global_script' in vardict:
      self.script.load( vardict['global_script'] )

    # re-enable updates and directly call for an update
    self.allow_updates = True
    self.update()

  def clearvars(self):
    self.channels.clear()
    self.waveforms.clear()
    self.signals.clear()
    self.script.set_text(default_script)


  def update(self):
    """
    This is the main callback function for 'changed' type signals.  This
    callback will collect the current inputs and send them to the processor.
    The processor will transform the descriptions into per-channel waveforms,
    plot them and send them to the backend drivers.
    """

    if not self.allow_updates:
      return

    print 'updating something...'

