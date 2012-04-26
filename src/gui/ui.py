# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gtk, gobject

import sys

# local packages
import about, configure, stores, edit
from plotter import Plotter
from packing import Args as PArgs, hpack, vpack, VBox
import storage
from notification import Notification

from .. import backend
from ..processor import Processor



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
from physical.unit import *
from physical.constant import *
from physical import unit

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

def notify_position(w):
  pos = w.get_position()
  sz  = w.get_size()
  return ( int(pos[0] + sz[0]*.5), pos[1] + sz[1] )

class ArbWave(gtk.Window):
  def __init__(self, parent=None):
    #create the toplevel window
    gtk.Window.__init__(self)
    self.set_title('Arbitrary Waveform Generator')
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      self.connect('destroy', lambda *w: gtk.main_quit())


    #  ###### SET UP THE UNDO/REDO STACK AND CALLBACKS ######
    self.notify = Notification( parent=self,
      get_position=lambda: notify_position(self),
    )
    self.undo = list()
    self.redo = list()
    self.connect('key-press-event', self.do_keypress)
    self.next_untested_undo = 0 # index of the last undo item that successfully
                                # updated hardware and plots


    # LOAD THE STORAGE
    self.plotter = Plotter( self )
    self.processor = Processor( self.plotter )
    self.script = stores.Script(
      '',
      title='Global Variables/Functions...',
      parent=self,
      add_undo=self.add_undo,
      changed=self.update,
    )
    self.channels = stores.Channels(
      row_changed=(self.channels_row_changed),
      row_deleted=(self.channels_row_deleted),
      row_inserted=(self.channels_row_inserted),
      rows_reordered=(self.channels_rows_reordered),
    )
    self.waveforms = stores.Waveforms( changed=self.update )
    self.signals = stores.Signals( changed=self.update )
    self.channel_editor = edit.Channels(
      channels=self.channels,
      processor=self.processor,
      parent=self,
      add_undo=self.add_undo )
    self.waveform_editor = \
      edit.Waveforms(self.waveforms, self.channels, self.add_undo)
    # simple variable to ensure that our signal handlers do not contest
    self.allow_updates = True

    # ensure that the default_script is executed for default the global env
    self.script.set_text( default_script )


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
    chew.add( self.channel_editor.view )
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
    wew.add( self.waveform_editor.view )
    wbox = gtk.EventBox()
    wbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16962,36237,65535))
    wbox.add(
      hpack(
        PArgs( vpack(wtools, PArgs(wlabel,False)), False),
        wew,
      )
    )


    self.plotter.canvas.set_size_request( 800, 200 )
    #self.canvas_scroll = gtk.HScale()

    top = gtk.HPaned()
    top.pack1( chbox, True, False )
    top.pack2( wbox, True, False )
    bottom = VBox()
    bottom.pack_start( self.plotter.canvas )
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
                 self.plotter.toolbar,
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

    def run_waveforms(action):
      def show_stopped():
        action.set_property('stock-id', gtk.STOCK_MEDIA_PLAY)

      # make sure that we switch the icons, and then update output
      if action.get_property('stock-id') == gtk.STOCK_MEDIA_PLAY:
        action.set_property('stock-id', gtk.STOCK_MEDIA_STOP)
      else:
        show_stopped()
        show_stopped = None

      # now update the output...
      self.update( toggle_run=True, show_stopped=show_stopped )

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
      'Run'       : run_waveforms,
      'About'     : lambda a: about.show(),
      'CH:Add'    : lambda a: self.channel_editor.insert_row(),
      'CH:Delete' : lambda a: self.channel_editor.delete_row(),
      'CH:Up'     : lambda a: sys.stderr.write('Move channel up\n'),
      'CH:Down'   : lambda a: sys.stderr.write('Move channel down\n'),
      'WF:Add:group': lambda a: self.waveform_editor.insert_waveform_group(),
      'WF:Add'    : lambda a: self.waveform_editor.insert_waveform(),
      'WF:Delete' : lambda a: self.waveform_editor.delete_row(),
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

  def clearundo(self):
    self.undo = list()  # remove all current undo items
    self.redo = list()  # remove all current undo items
    self.next_untested_undo = 0

  def setvars(self, vardict):
    self.clearundo()

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
    self.clearundo()
    self.channels.clear()
    self.waveforms.clear()
    self.signals.clear()
    self.script.set_text(default_script)


  def update(self, item=None, toggle_run=False, show_stopped=None):
    """
    This is the main callback function for 'changed' type signals.  This
    callback will collect the current inputs and send them to the processor.
    The processor will transform the descriptions into per-channel waveforms,
    plot them and send them to the backend drivers.

    item : should generally be one of [channels, waveforms, signals, script]

    show_stopped : if not None, then waveforms will be generated.  This should be a
    callable that will indicate back to the user that running has ceased.
    """

    if not self.allow_updates:
      return # updates temporarily disabled

    try:
      if item not in [
        None, self.channels, self.waveforms, self.signals, self.script,
      ]:
        raise TypeError('Unknown item sent to update()')

      assert show_stopped is None or callable(show_stopped), \
        'expected callable show_stopped'

      self.processor.update(
        ( self.channels.representation(),   item in [ None, self.channels] ),
        ( self.waveforms.representation(),  item in [ None, self.waveforms] ),
        ( self.signals.representation(),    item in [ None, self.signals] ),
        ( self.script.representation(),     item in [ None, self.script] ),
        toggle_run=toggle_run,
        show_stopped=show_stopped,
      )
      self.next_untested_undo = len(self.undo)
    except Exception, e:
      print e
      self.notify.show(
        '<span color="red"><b>Error</b>: \n' \
        '   Could not update output\n' \
        '   Number of changes since last successful update: {} \n' \
        '   {}\n' \
        '</span>\n' \
        .format(len(self.undo) - self.next_untested_undo,
                str(e).replace('<', '&lt;').replace('>', '&gt;')) )
      #raise e

  def channels_row_changed(self, model, path, iter):
    self.update(model)

  def channels_row_deleted(self, model, path):
    self.update(model)

  def channels_row_inserted(self, model, path, iter):
    self.update(model)

  def channels_rows_reordered(self, model, path, iter, new_order):
    self.update(model)

  def add_undo(self, undo_item ):
    self.undo.append( undo_item )
    self.redo = list()  # remove all current undo items

  def do_keypress(self, widget, event):
    """Implement keypress handlers on the main window"""
    if   event.state == gtk.gdk.CONTROL_MASK and event.keyval == 122:
      # Control-Z  :  UNDO
      try:
        change = self.undo.pop()
        change.undo()
        self.redo.append( change )
      except IndexError:
        pass
      return True
    elif event.state == gtk.gdk.CONTROL_MASK and event.keyval == 121:
      # Control-Y  :  REDO
      try:
        change = self.redo.pop()
        change.redo()
        self.undo.append( change )
      except IndexError:
        pass
      return True
