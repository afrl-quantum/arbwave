# vim: ts=2:sw=2:tw=80:nowrap
'''
Arbitrary waveform generator for digital and analog signals.
'''

import gtk, gobject
import logging

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
import embedded

from ..processor import Processor
from ..processor import default
from .. import backend
from .. import version
from .. import options



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
    <toolitem action='WF:Select'/>
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
		# if possible, the run function should return a value indicative of the
		# performance of the particular run.  Below is just a "random" example.
		import random
		return random.randint(0,100)

arbwave.add_runnable( 'Simple', SimpleRun() )
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
  s = edit.optimize.show.Show(
    columns=['Undefined'],
    title='Data Viewer',
    parent=parent
  )
  s.show()


class ArbWave(gtk.Window):
  TITLE = {False:'',True:'(Sim) '}[options.simulated] + 'Arbitrary Waveform Generator'
  ALL_ITEMS = -1

  def __init__(self, parent=None):
    #create the toplevel window
    gtk.Window.__init__(self)
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
    self.saved = True # Whether the config file loaded has been saved

    # simple variable to ensure that our signal handlers do not contest
    self.allow_updates = False

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
    self.waveforms = stores.WaveformsSet( changed=self.update )
    self.signals = stores.Signals( changed=self.update )
    self.devcfg  = stores.Generic( changed=self.update )
    self.clocks  = stores.Generic( changed=self.update )
    self.channel_editor = edit.Channels(
      channels=self.channels,
      processor=self.processor,
      parent=self,
      add_undo=self.add_undo )
    self.waveform_editor = edit.Waveforms(
      self.waveforms,
      self.channels, self, self.add_undo )

    self.allow_updates = True

    #  ###### SET UP THE PANEL #######
    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      logging.critical( 'building menus failed: %s', str(msg) )

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
    self.waveforms.connect_wf_change(
      lambda wf: wlabel.set_markup(
        'Waveforms (<b><span color="green">{}</span></b>)'.format(wf)
      )
    )


    self.plotter.canvas.set_size_request( 800, 200 )

    top = gtk.HPaned()
    top.pack1( chbox, True, False )
    top.pack2( wbox, True, False )
    self.shell = embedded.Shell_Gui(
      ui=self,
      get_globals=self.processor.get_globals,
      reset = self.processor.reset,
    )
    self.processor.connect_listener( self.shell.update_globals )
    self.shell_notebook = gtk.Notebook()
    self.shell_notebook.set_tab_border(0)
    self.shell_notebook.append_page( self.shell.gui, gtk.Label('Shell') )
    self.shell_notebook.set_tab_reorderable( self.shell.gui, True )

    def tab_tear( notebook, page, x, y ):
      notebook.remove_page( notebook.page_num(page) )
      if hasattr(page, 'orig_parent'):
        w = page.orig_parent
      else:
        w = gtk.Window()
      w.add( page )
      w.show()

    self.shell_notebook.connect('create-window', tab_tear)

    bottom = gtk.HPaned()
    bottom.pack1( self.shell_notebook )
    bottom.pack2( self.plotter.canvas )

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
    self.saved = True
    self.set_full_title()


  def __del__(self):
    # explicitly delete the processor
    logging.debug( 'trying to del the proc.' )
    self.processor.__del__() # not sure why "del ui" below is not working!
    del self.processor


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
        '_About', '<shift><control>A',             # label, accelerator
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
      except Exception, e: self.notify.show( str(e) )

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'New'       : lambda a: self.clearvars(do_update=True),
      'Open'      : ( show_exception, storage.gtk_tools.gtk_open_handler, self, default.get_globals() ),
      'Save'      : lambda a: self.save(),
      'SaveAs'    : lambda a: self.save(True),
      'Quit'      : lambda a: self.destroy(),
      'Configure' : lambda a: configure.show(self, self),
      'Script'    : lambda a: self.script.edit(notebook=self.shell_notebook),
      'Run'       : lambda a: self.update(toggle_run=True),
      'ViewData'  : lambda a: show_data_viewer(self),
      'About'     : lambda a: about.show(),
      'VGens'     : lambda a: tips.show_generators(self),
      'arbhelp'   : lambda a: tips.show_arbwavefunctions(self),
      'CH:Add'    : lambda a: self.channel_editor.insert_row(),
      'CH:Delete' : lambda a: self.channel_editor.delete_row(),
      'WF:Add'    : lambda a: self.waveform_editor.insert_waveform(),
      'WF:Delete' : lambda a: self.waveform_editor.delete_row(),
      'WF:Select' : self.select_waveform,
    }

    return action_group

  def save(self, *args):
    storage.gtk_tools.gtk_save_handler(None, self, *args)

  def select_waveform(self, action):
    D = edit.waveformsset.Dialog( self.waveforms, parent=self, dialog=True )
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

    self.clearundo()

    # suspend all updates
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
      logging.debug('devices.load(...)..........')
      self.devcfg.load( vardict['devices'] )
      logging.debug('devices.load(...) finished.')

    if 'runnable_settings' in vardict:
      logging.debug('runnable_settings.load(...)..........')
      self.runnable_settings = vardict['runnable_settings']
      logging.debug('runnable_settings.load(...) finished.')

    # re-enable updates and directly call for an update
    self.unpause()
    self.update(self.ALL_ITEMS)

  def clearvars(self, do_update=False):
    # suspend all updates
    self.pause()

    logging.debug('clearundo....')
    self.clearundo()
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
    self.set_config_file('')
    self.saved = True
    logging.debug('runnable_settings.clear()....')
    self.runnable_settings.clear()

    # re-enable updates
    self.unpause()
    # directly call for an update (?)
    if do_update:
      self.update(self.ALL_ITEMS)


  def set_file_saved(self, yes=True):
    self.saved = yes
    self.set_full_title()


  def set_config_file(self,f):
    self.config_file = f
    default.registered_globals['__file__'] = f
    self.set_full_title()

  def set_full_title(self):
    star = {True:'', False:'*'}[self.saved]
    self.set_title( self.TITLE + ':  ' + self.config_file + star )


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
        self.channels, self.waveform_editor.get_waveform(), self.script,
      ]:
        raise TypeError('Unknown item sent to update()')

      self.processor.update(
        ( self.devcfg.representation(),    item in [ self.ALL_ITEMS, self.devcfg] ),
        ( self.clocks.representation(),    item in [ self.ALL_ITEMS, self.clocks] ),
        ( self.signals.representation(),   item in [ self.ALL_ITEMS, self.signals] ),
        ( self.channels.representation(),  item in [ self.ALL_ITEMS, self.channels] ),
        ( self.waveform_editor.get_waveform().representation(store_path=True),
                                           item in [ self.ALL_ITEMS, self.waveform_editor.get_waveform()] ),
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
    self.saved = False # mark the config file as not having been saved
    self.set_full_title()

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
