# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gtk, gobject

import sys
import traceback

# local packages
import about, tips, configure, stores, edit
import edit.optimize
import edit.loop
from plotter import Plotter
from packing import Args as PArgs, hpack, vpack, VBox
import storage
from notification import Notification

from ..processor import Processor
from ..processor import default
from .. import backend
from .. import version



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
    <menu action='ViewMenu'>
      <menuitem action='ViewData'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
      <menuitem action='VGens'/>
      <menuitem action='arbhelp'/>
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
  </toolbar>
  <toolbar  name='WaveformToolBar'>
    <toolitem action='WF:Add'/>
    <toolitem action='WF:Delete'/>
  </toolbar>
</ui>'''

default_script = """\
# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from physical.unit import *
from physical.constant import *
from physical import unit
import arbwave

class SimpleRun(arbwave.Runnable):
	def run(self):
		arbwave.update()

arbwave.add_runnable( 'Simple', SimpleRun() )
"""

def notify_position(w):
  pos = w.get_position()
  sz  = w.get_size()
  return ( int(pos[0] + sz[0]*.5), pos[1] + sz[1] )


def finished(*args, **kwargs):
  """
  Finish everything:  close drivers, close windows...
  """
  backend.unload_all()
  gtk.main_quit()


def show_data_viewer(parent):
  s = edit.optimize.show.Show(
    columns=['Undefined'],
    title='Data Viewer',
    parent=parent
  )
  s.show()


class ArbWave(gtk.Window):
  TITLE = 'Arbitrary Waveform Generator'
  ALL_ITEMS = -1

  def __init__(self, parent=None):
    #create the toplevel window
    gtk.Window.__init__(self)
    self.set_title( self.TITLE )
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      self.connect('destroy', finished)


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
    self.set_config_file('')
    self.plotter = Plotter( self )
    self.processor = Processor( self )
    self.script = stores.Script(
      default_script,
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
    self.devcfg  = stores.Generic( changed=self.update )
    self.clocks  = stores.Generic( changed=self.update )
    self.channel_editor = edit.Channels(
      channels=self.channels,
      processor=self.processor,
      parent=self,
      add_undo=self.add_undo )
    self.waveform_editor = \
      edit.Waveforms(self.waveforms, self.channels, self, self.add_undo)
    # simple variable to ensure that our signal handlers do not contest
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


    self.runnable_settings = dict()
    self.runnables = set()
    self.runnable_tree = gtk.TreeStore(str,str)
    self.run_combo = gtk.ComboBox(self.runnable_tree)
    edit.helpers.prep_combobox_for_tree(self.run_combo,True)
    self.update_runnables([])
    self.run_combo.set_size_request(10,-1)


    self.add( vpack(
        PArgs( merge.get_widget('/MenuBar'), False, False, 0 ),
        PArgs( # MENU BAR LOCATION
          hpack( merge.get_widget('/ToolBar'),
                 PArgs(gtk.VSeparator(), False),
                 PArgs(gtk.VSeparator(), False),
                 self.run_combo,
                 PArgs(gtk.VSeparator(), False),
                 PArgs(gtk.VSeparator(), False),
                 self.plotter.toolbar,
          ), False ),
        body
    ))

    self.show_all()

    # ensure that the default_script is executed for default the global env
    self.processor.exec_script( default_script )


  def update_runnables(self, runnables):
    T = self.runnable_tree
    active_i = self.run_combo.get_active_iter()
    active_txt = 'Default'
    if active_i:
      active_txt = T[active_i][1]
    active_i = None

    self.runnables = set(runnables)
    T.clear()
    for r in self.runnables:
      i = T.append( None, (r,r) )
      if r == active_txt:
        active_i = i

      if r == 'Default':
        continue

      for op in ['Loop', 'Optimize']:
        r_op = r + ':  ' + op
        ii = T.append( i, (r,r_op) )
        if r_op == active_txt:
          active_i = ii

    if not len(T):
      return

    if not active_i:
      active_i = T.get_iter(0)
    self.run_combo.set_active_iter(active_i)

  def get_active_runnable(self):
    T = self.runnable_tree
    active_i = self.run_combo.get_active_iter()
    if active_i:
      runnable  = self.runnable_tree[ active_i ][0]
      run_label = self.runnable_tree[ active_i ][1]
      if 'Loop' in run_label:
        return runnable, edit.loop.Make(self, run_label, self.runnable_settings)
      elif 'Optimize' in run_label:
        return runnable, edit.optimize.Make(self, run_label, self.runnable_settings)
      else:
        return runnable, None
    return 'Default', None

  def create_action_group(self):
    # GtkActionEntry
    entries = (
      ( 'FileMenu', None, '_File' ),               # name, stock id, label
      ( 'EditMenu', None, '_Edit' ),               # name, stock id, label
      ( 'ViewMenu', None, '_View' ),               # name, stock id, label
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
      ( 'ViewData', gtk.STOCK_EDIT,                # name, stock id
        'Data Viewer', None,                       # label, accelerator
        'View saved text data...',# tooltip
        self.activate_action ),
      ( 'About', None,                             # name, stock id
        '_About', '<control>A',                    # label, accelerator
        'About',                                   # tooltip
        self.activate_action ),
      ( 'VGens', None,                             # name, stock id
        'Value _Generators', '<control>G',         # label, accelerator
        'Known value generator functions',         # tooltip
        self.activate_action ),
      ( 'arbhelp', None,                           # name, stock id
        'Arbwave Script _Functions', '',           # label, accelerator
        'Scripting functions of arbwave module',   # tooltip
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

      # WAVEFORM EDITOR
      ( 'WF:Add', gtk.STOCK_ADD,                   # name, stock id
        None, None,                                # label, accelerator
        'Add waveform element after '
        'current waveform element',                # tooltip
        self.activate_action ),
      ( 'WF:Delete', gtk.STOCK_DELETE,             # name, stock id
        None, None,                                # label, accelerator
        'Delete current waveform element',         # tooltip
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

    #     # Create the menubar and toolbar
    action_group = gtk.ActionGroup('ArbWaveGUIActions')
    action_group.add_actions(entries)
    action_group.add_toggle_actions(toggle_entries)
    self.run_action = action_group.get_action('Run')

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'New'       : lambda a: self.clearvars(),
      'Open'      : ( storage.gtk_tools.gtk_open_handler, self, default.get_globals() ),
      'Save'      : ( storage.gtk_tools.gtk_save_handler, self ),
      'SaveAs'    : ( storage.gtk_tools.gtk_save_handler, self, True),
      'Quit'      : lambda a: self.destroy(),
      'Configure' : lambda a: configure.show(self, self),
      'Script'    : lambda a: self.script.edit(),
      'Run'       : lambda a: self.update(toggle_run=True),
      'ViewData'  : lambda a: show_data_viewer(self),
      'About'     : lambda a: about.show(),
      'VGens'     : lambda a: tips.show_generators(self),
      'arbhelp'   : lambda a: tips.show_arbwavefunctions(self),
      'CH:Add'    : lambda a: self.channel_editor.insert_row(),
      'CH:Delete' : lambda a: self.channel_editor.delete_row(),
      'WF:Add'    : lambda a: self.waveform_editor.insert_waveform(),
      'WF:Delete' : lambda a: self.waveform_editor.delete_row(),
    }

    return action_group

  def show_stopped(self):
    if self.run_action.get_property('stock-id') != gtk.STOCK_MEDIA_PLAY:
      self.run_action.set_property('stock-id', gtk.STOCK_MEDIA_PLAY)

  def show_started(self):
    if self.run_action.get_property('stock-id') != gtk.STOCK_MEDIA_STOP:
      self.run_action.set_property('stock-id', gtk.STOCK_MEDIA_STOP)

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
      'devices'   : self.devcfg.representation(),
      'clocks'    : self.clocks.representation(),
      'global_script': self.script.representation(),
      'channels'  : self.channels.representation(),
      'waveforms' : self.waveforms.representation(),
      'signals'   : self.signals.representation(),
      'version'   : version.version(),
      'runnable_settings' : self.runnable_settings,
    }

  def clearundo(self):
    self.undo = list()  # remove all current undo items
    self.redo = list()  # remove all current undo items
    self.next_untested_undo = 0


  def pause(self):
    self.allow_updates = False


  def unpause(self):
    self.allow_updates = True


  def setvars(self, vardict):
    # first check the version of the configuration file
    if 'version' not in vardict or not version.supported( vardict['version'] ):
      v = vardict.get('version','UNKNOWN')
      self.notify.show(
        '<span color="red"><b>Error</b>:  \n' \
        '   Config file version:'        '\n' \
        '     <span color="blue">{}</span>\n' \
        '   older than'                  '\n' \
        '     <span color="blue">{}</span>\n' \
        '   Cannot load!'                '\n' \
        '</span>'                        '\n' \
        .format(v, version.last_key_version()) )
      raise RuntimeError('Loading unsupported config file version')

    self.clearundo()

    # suspend all updates
    self.pause()

    if 'channels' in vardict:
      self.channels.load( vardict['channels'] )

    if 'waveforms' in vardict:
      self.waveforms.load( vardict['waveforms'] )

    if 'signals' in vardict:
      self.signals.load( vardict['signals'] )

    if 'global_script' in vardict:
      self.script.load( vardict['global_script'] )

    if 'clocks' in vardict:
      self.clocks.load( vardict['clocks'] )

    if 'devices' in vardict:
      self.devcfg.load( vardict['devices'] )

    if 'runnable_settings' in vardict:
      self.runnable_settings = vardict['runnable_settings']

    # re-enable updates and directly call for an update
    self.unpause()
    self.update(self.ALL_ITEMS)

  def clearvars(self):
    # suspend all updates
    self.pause()

    self.clearundo()
    self.channels.clear()
    self.waveforms.clear()
    self.signals.clear()
    self.script.set_text(default_script)
    self.clocks.clear()
    self.devcfg.clear()
    self.set_config_file('')
    self.runnable_settings.clear()

    # re-enable updates and directly call for an update
    self.unpause()
    self.update(self.ALL_ITEMS)


  def set_config_file(self,f):
    self.config_file = f
    self.set_title( self.TITLE + ':  ' + f )
    default.registered_globals['__file__'] = f


  def get_config_file(self):
    return self.config_file


  def update(self, item=None, toggle_run=False):
    """
    This is the main callback function for 'changed' type signals.  This
    callback will collect the current inputs and send them to the processor.
    The processor will transform the descriptions into per-channel waveforms,
    plot them and send them to the backend drivers.

    item : should generally be one of
           [devcfg, clocks, signals, channels, waveforms, script]
    """

    if not self.allow_updates:
      return # updates temporarily disabled

    try:
      if item not in [
        self.ALL_ITEMS, None, self.devcfg, self.clocks, self.signals,
        self.channels, self.waveforms, self.script,
      ]:
        raise TypeError('Unknown item sent to update()')

      self.processor.update(
        ( self.devcfg.representation(),    item in [ self.ALL_ITEMS, self.devcfg] ),
        ( self.clocks.representation(),    item in [ self.ALL_ITEMS, self.clocks] ),
        ( self.signals.representation(),   item in [ self.ALL_ITEMS, self.signals] ),
        ( self.channels.representation(),  item in [ self.ALL_ITEMS, self.channels] ),
        ( self.waveforms.representation(store_path=True),
                                           item in [ self.ALL_ITEMS, self.waveforms] ),
        ( self.script.representation(),    item in [ self.ALL_ITEMS, self.script] ),
        toggle_run=toggle_run,
      )
      self.next_untested_undo = len(self.undo)
    except Exception, e:
      traceback.print_exc()
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
