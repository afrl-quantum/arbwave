# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, Gdk as gdk, GObject as gobject
import logging
from copy import deepcopy

import traceback

# local packages
from . import about, tips, configure, stores, edit
from .edit import optimize as edit_optimize
from .edit import loop as edit_loop
from .plotter import Plotter
from .packing import Args as PArgs, hpack, vpack, VBox
from . import storage
from .notification import Notification
from . import embedded

from ..tools.config_template_update import recursive_update
from ..tools.gui_callbacks import do_gui_operation
from ..processor import default
from .. import backend
from .. import version
from .. import options
from . import hosts_changed
from .dataviewer import DataViewer



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
      <menuitem action='Undo'/>
      <menuitem action='Redo'/>
      <menuitem action='ShowUndo'/>
      <separator/>
      <menuitem action='Configure'/>
      <menuitem action='Script'/>
    </menu>
    <menu action='ViewMenu'>
      <menuitem action='ViewData'/>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='About'/>
      <menuitem action='autovars'/>
      <menuitem action='Exprs'/>
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
    <toolitem action='WF:Select'/>
  </toolbar>
</ui>'''

default_script = """\
# This script sets global variables and/or functions.
# All other scripts and processing will be done in this context.
from physical.unit import *
from physical.constant import *
from physical import unit
import Arbwave

class SimpleRun(Arbwave.Runnable):
	def run(self):
		Arbwave.update()
		# if possible, the run function should return a value indicative of the
		# performance of the particular run.  Below is just a "random" example.
		import random
		return random.randint(0,100)

Arbwave.add_runnable( 'Simple', SimpleRun() )
"""

def notify_position(w):
  pos = w.get_position()
  sz  = w.get_size()
  return ( int(pos[0] + sz[0]*.5), pos[1] + sz[1] )


def finished(ui, *args, **kwargs):
  """
  Finish everything:  close drivers, close windows...
  """
  backend.unload_all()
  gtk.main_quit()
  logging.debug( 'trying to del the ui: %s', repr(ui) )
  ui.__del__() # not sure why "del ui" below is not working!
  del ui


def show_data_viewer(parent):
  s = DataViewer()
  s.show()


class ArbWave(gtk.Window):
  TITLE = {False:'',True:'(Sim) '}[options.simulated] + 'Arbitrary Waveform Generator'

  run_in_ui_thread = staticmethod(do_gui_operation)

  def __init__(self, parent=None, *, init_new=False):
    # delay this import to try and separate arbwave submodules
    from ..processor.for_gui import Processor

    #create the toplevel window
    super(ArbWave,self).__init__()
    try:
      self.set_screen(parent.get_screen())
    except AttributeError:
      self.connect('destroy', finished)
      def quit():
        """Quit Arbwave"""
        finished(self)
      self.quit = quit


    #  ###### SET UP THE UNDO/REDO STACK AND CALLBACKS ######
    self.notify = Notification( parent=self,
      get_position=lambda: notify_position(self),
    )
    self.undo = stores.Undo(parent=self,
      changed=lambda:self.set_file_saved(False),
    )
    self.connect('key-press-event', self.do_keypress)

    # simple variable to ensure that our signal handlers do not contest
    self.allow_updates = False

    # LOAD THE STORAGE
    self.set_file_saved(filename='')
    self.plotter = Plotter( self )
    self.processor = Processor( ui=self )
    self.script = stores.Script(
      default_script,
      title='Global Variables/Functions...',
      parent=self,
      add_undo=self.undo.add,
      changed=self.update,
    )
    self.channels = stores.Channels(
      row_changed=(self.channels_row_changed),
      row_deleted=(self.channels_row_deleted),
      row_inserted=(self.channels_row_inserted),
      rows_reordered=(self.channels_rows_reordered),
    )
    self.waveforms  = stores.WaveformsSet( changed=self.update )
    self.hosts      = stores.Hosts       ( changed=self.update )
    self.signals    = stores.Signals     ( changed=self.update )
    self.devcfg     = stores.Generic     ( changed=self.update )
    self.clocks     = stores.Generic     ( changed=self.update )
    self.channel_editor = edit.Channels(
      channels=self.channels,
      processor=self.processor,
      parent=self,
      add_undo=self.undo.add )
    self.waveform_editor = edit.Waveforms(
      self.waveforms,
      self.channels, self, self.undo.add )

    self.allow_updates = True

    #  ###### SET UP THE PANEL #######
    merge = gtk.UIManager()
    self.ui_manager = merge
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError as msg:
      logging.critical( 'building menus failed: %s', str(msg) )

    chlabel = gtk.Label('Channels')
    chlabel.set_property('angle', 90)
    chtools = merge.get_widget('/ChannelToolBar')
    chtools.set_property('orientation', gtk.Orientation.VERTICAL )
    chtools.set_property('icon-size', gtk.IconSize.MENU)
    chtools.set_property('toolbar-style', gtk.ToolbarStyle.ICONS)
    chew = gtk.ScrolledWindow()
    chew.set_size_request( -1, -1 )
    chew.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    chew.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    chew.add( self.channel_editor.view )
    chbox = gtk.EventBox()
    chbox.modify_bg(gtk.StateType.NORMAL, gdk.Color(16962,36237,65535))
    chbox.add(
      hpack(
        PArgs( vpack(chtools, PArgs(chlabel,False)), False),
        chew,
      )
    )


    wlabel = gtk.Label('Waveforms')
    wlabel.set_property('angle', 90)
    wtools = merge.get_widget('/WaveformToolBar')
    wtools.set_property('orientation', gtk.Orientation.VERTICAL )
    wtools.set_property('icon-size', gtk.IconSize.MENU)
    wtools.set_property('toolbar-style', gtk.ToolbarStyle.ICONS)
    wew = gtk.ScrolledWindow()
    wew.set_size_request(-1,225)
    wew.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    wew.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    wew.add( self.waveform_editor.view )
    wbox = gtk.EventBox()
    wbox.modify_bg(gtk.StateType.NORMAL, gdk.Color(16962,36237,65535))
    wbox.add(
      hpack(
        PArgs( vpack(wtools, PArgs(wlabel,False)), False),
        wew,
      )
    )
    self.waveforms.connect_wf_change(
      lambda wf: wlabel.set_markup(
        'Waveforms (<b><span color="green">{}</span></b>)'.format(wf)
      )
    )


    self.plotter.canvas.set_size_request( -1, 200 )

    top = gtk.HPaned()
    top.pack1( chbox, True, False )
    top.pack2( wbox, True, False )
    self.shell = embedded.Python(
      ui=self,
      get_globals=self.processor.get_globals,
      reset = self.processor.reset,
    )
    self.processor.connect_listener( self.shell.update_globals )
    shell_sb = gtk.ScrolledWindow()
    shell_sb.add(self.shell)

    self.shell_notebook = gtk.Notebook()
    self.shell_notebook.set_property('border-width',0)
    self.shell_notebook.append_page(shell_sb, gtk.Label('Arbwave Command Line'))
    self.shell_notebook.set_tab_reorderable( shell_sb, True )

    def tab_tear( notebook, page, x, y ):
      notebook.detach_tab(page)
      if hasattr(page, 'orig_parent'):
        w = page.orig_parent
      else:
        w = gtk.Window()
      w.add( page )
      w.show()

    self.shell_notebook.connect('create-window', tab_tear)

    bottom = gtk.HPaned()
    bottom.pack1( self.shell_notebook, resize=True )
    bottom.pack2( self.plotter.canvas, resize=True )
    bottom.set_position(182)

    body = gtk.VPaned()
    body.pack1( top, True )
    body.pack2( bottom, True )


    self.runnable_settings = dict()
    self.runnables = set()
    self.runnable_tree = gtk.TreeStore(str,str)
    self.run_combo = gtk.ComboBox.new_with_model(self.runnable_tree)
    edit.helpers.prep_combobox_for_tree(self.run_combo,True)
    self.update_runnables([])
    self.run_combo.set_size_request(10,-1)


    self.add( vpack(
        PArgs( merge.get_widget('/MenuBar'), False, False, 0 ),
        PArgs( # MENU BAR LOCATION
          hpack( PArgs(merge.get_widget('/ToolBar'),False),
                 PArgs(gtk.VSeparator(), False),
                 PArgs(gtk.VSeparator(), False),
                 PArgs(self.run_combo,   False),
                 PArgs(gtk.VSeparator(), False),
                 PArgs(gtk.VSeparator(), False),
                 self.plotter.toolbar,
          ), False ),
        body
    ))

    self.set_size_request( 780, -1 )

    self.show_all()

    # ensure that the default_script is executed for default the global env
    self.processor.exec_script( default_script )
    self.set_file_saved()

    if init_new:
      self.clearvars(do_update=True)


  def __del__(self):
    # explicitly delete the processor
    logging.debug( 'trying to del the proc.' )
    self.processor.__del__() # not sure why "del ui" below is not working!
    del self.processor


  @property
  def ALL_ITEMS(self):
    return set([
      self.hosts, self.devcfg, self.clocks, self.signals, self.channels,
      self.waveform_editor.get_waveform(), self.script,
    ])



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
        return runnable, edit_loop.Make(self, run_label, self.runnable_settings)
      elif 'Optimize' in run_label:
        return runnable, edit_optimize.Make(self, run_label, self.runnable_settings)
      else:
        return runnable, None
    return 'Default', None

  def update_t_max(self, t_max):
    """
    Update the processors expectation of the waveform duration.  This
    information is used to help properly close down runnables and not wait
    beyond the expected duration.
    """
    # this does *not* have to run in the gui thread and is already protected by
    # a thread lock in the processor.
    self.processor.t_max = t_max

  def create_action_group(self):
    # GtkActionEntry
    entries = (
      ( 'FileMenu', None, '_File' ),               # name, stock id, label
      ( 'EditMenu', None, '_Edit' ),               # name, stock id, label
      ( 'ViewMenu', None, '_View' ),               # name, stock id, label
      ( 'HelpMenu', None, '_Help' ),               # name, stock id, label
      ( 'New', gtk.STOCK_NEW,                      # name, stock id
        '_New', '<shift><control>N',               # label, accelerator
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
      ( 'Undo', gtk.STOCK_UNDO,                    # name, stock id
        '_Undo', '<control>z',                     # label, accelerator
        'Undo last change',                        # tooltip
        self.activate_action ),
      ( 'Redo', gtk.STOCK_REDO,                    # name, stock id
        '_Redo', '<control>y',                     # label, accelerator
        'Redo last undone change',                 # tooltip
        self.activate_action ),
      ( 'ShowUndo', gtk.STOCK_INDEX,               # name, stock id
        '_Show undo/redo', None,                   # label, accelerator
        'Show undo/redo stacks',                   # tooltip
        self.activate_action ),
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
        '_About', '<shift><control>A',             # label, accelerator
        'About',                                   # tooltip
        self.activate_action ),
      ( 'autovars', None,                          # name, stock id
        'Automatic Waveform _Varaibles', '',       # label, accelerator
        'Automatically generated local waveform variables', # tooltip
        self.activate_action ),
      ( 'Exprs', None,                             # name, stock id
        'Value _Expressions', '<shift><control>E', # label, accelerator
        'Symbolic time-varying value expressions', # tooltip
        self.activate_action ),
      ( 'VGens', None,                             # name, stock id
        'Value _Generators', '<shift><control>G',  # label, accelerator
        'Known value generator functions',         # tooltip
        self.activate_action ),
      ( 'arbhelp', None,                           # name, stock id
        'Arbwave Script _Functions', '',           # label, accelerator
        'Scripting functions of Arbwave module',   # tooltip
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
      ( 'WF:Select', gtk.STOCK_INDEX,              # name, stock id
        None, None,                                # label, accelerator
        'Select entire waveform from list',        # tooltip
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

    def show_exception( action, fun, *args, **kwargs ):
      try: fun( action, *args, **kwargs )
      except Exception as e: self.notify.show( str(e) )

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'New'       : lambda a: self.clearvars(do_update=True),
      'Open'      : ( show_exception, storage.gtk_tools.gtk_open_handler, self, default.get_globals() ),
      'Save'      : lambda a: self.save(),
      'SaveAs'    : lambda a: self.save(True),
      'Quit'      : lambda a: self.destroy(),
      'Undo'      : lambda a: self.undo.undo(),
      'Redo'      : lambda a: self.undo.redo(),
      'ShowUndo'  : lambda a: self.undo.show(),
      'Configure' : lambda a: configure.show(self, self),
      'Script'    : lambda a: self.script.edit(notebook=self.shell_notebook),
      'Run'       : lambda a: self.update(toggle_run=True),
      'ViewData'  : lambda a: show_data_viewer(self),
      'About'     : lambda a: about.show(),
      'autovars'  : lambda a: tips.show_autovars(self),
      'Exprs'     : lambda a: tips.show_expressions(self),
      'VGens'     : lambda a: tips.show_generators(self),
      'arbhelp'   : lambda a: tips.show_arbwavefunctions(self),
      'CH:Add'    : lambda a: self.channel_editor.insert_row(self),
      'CH:Delete' : lambda a: self.channel_editor.delete_row(),
      'WF:Add'    : lambda a: self.waveform_editor.insert_waveform(),
      'WF:Delete' : lambda a: self.waveform_editor.delete_row(),
      'WF:Select' : self.select_waveform,
    }

    return action_group

  def save(self, *args):
    storage.gtk_tools.gtk_save_handler(None, self, *args)

  def select_waveform(self, action):
    D = edit.waveformsset.Dialog(self.waveforms, parent=self)
    D.show()

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
    """
    Used to provide data to save to Arbwave configuration file.
    """
    return {
      'hosts'     : self.hosts.representation(),
      'devices'   : self.devcfg.representation(),
      'clocks'    : self.clocks.representation(),
      'global_script': self.script.representation(),
      'channels'  : self.channels.representation(),
      'waveforms' : self.waveforms.representation(),
      'signals'   : self.signals.representation(),
      'version'   : version.version(),
      'runnable_settings' : self.runnable_settings,
    }


  def pause(self):
    self.allow_updates = False


  def unpause(self):
    self.allow_updates = True


  def setvars(self, vardict):
    # first check the version of the configuration file
    v = vardict.get('version','UNKNOWN')
    conversions = version.conversion_path( v )
    if not conversions:
      self.notify.show(
        '<span color="red"><b>Error</b>:  \n' \
        '   No upgrade path for:'        '\n' \
        '   Config file version'         '\n' \
        '     <span color="blue">{}</span>\n' \
        '   to current version'          '\n' \
        '     <span color="blue">{}</span>\n' \
        '   Cannot load!'                '\n' \
        '</span>'                        '\n' \
        .format(v, version.get_file_version()) )
      raise RuntimeError('Loading unsupported config file version')

    for c in conversions:
      vardict = c( vardict )

    self.undo.clear()

    # suspend all updates
    self.pause()

    if 'hosts' in vardict:
      logging.debug('hosts.load(%s)', vardict['hosts'])
      self.hosts.load( vardict['hosts'] )
      logging.debug('hosts.load(...) finished.')

    # we'll update hosts by themselves first
    self.unpause()
    self.update(self.hosts)

    # suspend again
    self.pause()

    if 'channels' in vardict:
      logging.debug('channels.load(...)..........')
      self.channels.load( vardict['channels'] )
      logging.debug('channels.load(...) finished.')

    if 'waveforms' in vardict:
      logging.debug('waveforms.load(...)..........')
      self.waveforms.load( vardict['waveforms'] )
      logging.debug('waveforms.load(...) finished.')

    if 'signals' in vardict:
      logging.debug('signals.load(...)..........')
      self.signals.load( vardict['signals'] )
      logging.debug('signals.load(...) finished.')

    if 'global_script' in vardict:
      logging.debug('globals_script.load(...)..........')
      self.script.load( vardict['global_script'] )
      logging.debug('globals_script.load(...) finished.')

    if 'clocks' in vardict:
      logging.debug('clocks.load(...)..........')
      self.clocks.load( vardict['clocks'] )
      logging.debug('clocks.load(...) finished.')

    if 'devices' in vardict:
      # we are going to attempt to allow device backends to add configuration
      # items without requiring a file-version upgrade.  This should _only_ be
      # done if items are simply added.  If they are changed or removed, a
      # file-version upgrade must be implemented.
      all_devices = backend.get_devices_attrib(
        'config_template',
        devices=set(vardict['devices'].keys()),
      )
      device_config = dict()
      for devname, devcfg in vardict['devices'].items():
        D = all_devices[devname]['config_template']
        recursive_update(D, devcfg)
        device_config[devname] = D

      logging.debug('devices.load(...)..........')
      self.devcfg.load(device_config)
      logging.debug('devices.load(...) finished.')

    if 'runnable_settings' in vardict:
      logging.debug('runnable_settings.load(...)..........')
      self.runnable_settings = vardict['runnable_settings']
      logging.debug('runnable_settings.load(...) finished.')

    self.undo.clear()

    # re-enable updates and directly call for an update
    self.unpause()
    self.update(*(self.ALL_ITEMS - set([self.hosts])))

  def clearvars(self, do_update=False):
    # suspend all updates
    self.pause()

    logging.debug('hosts.reset_to_default()....')
    self.hosts.reset_to_default()
    logging.debug('channels.clear()....')
    self.channels.clear()
    logging.debug('waveforms.clear()....')
    self.waveforms.clear()
    logging.debug('signals.clear()....')
    self.signals.clear()
    logging.debug('script.set_text(default_script)....')
    self.script.set_text(default_script)
    logging.debug('clocks.clear()....')
    self.clocks.clear()
    logging.debug('devcfg.clear()....')
    self.devcfg.clear()
    logging.debug('runnable_settings.clear()....')
    self.runnable_settings.clear()

    self.set_file_saved(filename='')
    self.undo.clear()

    # re-enable updates
    self.unpause()
    # directly call for an update (?)
    if do_update:
      self.update(*self.ALL_ITEMS)


  def set_file_saved(self, yes=True, filename=None):
    if filename is not None:
      self.config_file = filename
      default.registered_globals['__file__'] = filename

    if yes is not None:
      self.saved = yes
    star = {True:'', False:'*'}[self.saved]
    self.set_title( self.TITLE + ':  ' + self.config_file + star )


  def get_config_file(self):
    return self.config_file


  def update(self, *items, toggle_run=False):
    """
    This is the main callback function for 'changed' type signals.  This
    callback will collect the current inputs and send them to the processor.
    The processor will transform the descriptions into per-channel waveforms,
    plot them and send them to the backend drivers.

    items : should contain one or more of
           [hosts, devcfg, clocks, signals, channels, waveforms, script]
    """

    if not self.allow_updates:
      return # updates temporarily disabled

    items = set(items)

    try:
      if items - self.ALL_ITEMS:
        raise TypeError('Unknown item(s) sent to update(): {}'.format(items))

      self.processor.update(
        ( self.hosts.representation(),    self.hosts in items ),
        ( self.devcfg.representation(),   self.devcfg in items ),
        ( self.clocks.representation(),   self.clocks in items ),
        ( self.signals.representation(),  self.signals in items ),
        ( self.channels.representation(1),self.channels in items ),
        ( self.waveform_editor.get_waveform().representation(store_path=True),
                                          self.waveform_editor.get_waveform() in items ),
        ( self.script.representation(),   self.script in items ),
        toggle_run=toggle_run,
      )
      self.undo.mark_good()
    except Exception as e:
      traceback.print_exc()
      self.notify.show(
        '<span color="red"><b>Error</b>: \n' \
        '   Could not update output\n' \
        '   Number of changes since last successful update: {} \n' \
        '   {}\n' \
        '</span>\n' \
        .format(self.undo.number_failed,
                str(e).replace('<', '&lt;').replace('>', '&gt;')) )
      #raise e
    if items.intersection([self.hosts, self.devcfg]):
      # callbacks for host changes...
      hosts_changed.callback()

  def channels_row_changed(self, model, path, iter):
    self.update(model)

  def channels_row_deleted(self, model, path):
    self.update(model)

  def channels_row_inserted(self, model, path, iter):
    self.update(model)

  def channels_rows_reordered(self, model, path, iter, new_order):
    self.update(model)

  def do_keypress(self, widget, event):
    """Implement keypress handlers on the main window"""
    if   event.state & gdk.ModifierType.CONTROL_MASK and event.keyval == gdk.KEY_z:
      # Control-Z  :  UNDO
      self.undo.undo()
      return True
    elif event.state & gdk.ModifierType.CONTROL_MASK and event.keyval == gdk.KEY_y:
      # Control-Y  :  REDO
      self.undo.redo()
      return True
