# vim: ts=2:sw=2:tw=80:nowrap

import gtk, sys
import gobject

from ..packing import Args as PArgs, VBox, hpack, vpack
from .. import edit
from ... import backend
from ...tools.signal_graphs import accessible_clocks

ui_info = \
'''<ui>
  <toolbar  name='SignalToolBar'>
    <toolitem action='SIG:Add'/>
    <toolitem action='SIG:Delete'/>
    <separator/>
    <toolitem action='SIG:Up'/>
    <toolitem action='SIG:Down'/>
  </toolbar>
  <toolbar  name='ClockToolBar'>
    <toolitem action='CLK:Add'/>
    <toolitem action='CLK:Delete'/>
  </toolbar>
  <toolbar  name='DevToolBar'>
    <toolitem action='DEV:Add'/>
    <toolitem action='DEV:Delete'/>
  </toolbar>
  <toolbar  name='HostsToolBar'>
    <toolitem action='BKD:Add'/>
    <toolitem action='BKD:Delete'/>
  </toolbar>
</ui>'''

class ConfigDialog(gtk.Dialog):
  def __init__(self, win, store):
    gtk.Dialog.__init__(self,
      'Configure Signals/Triggers, ...',win,
      gtk.DIALOG_DESTROY_WITH_PARENT,
      (gtk.STOCK_OK, gtk.RESPONSE_OK,
       gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
    )


    # LOAD THE STORAGE
    self.store = store
    self.signal_editor = edit.signals.create(store.signals)
    self.devcfg_editor = edit.Generic(store.devcfg,
                                      range_factory=RangeFactory(store,False))
    self.clock_editor  = edit.Generic( store.clocks,
                                      range_factory=RangeFactory(store,True))
    self.hosts         = edit.hosts.create(store.hosts)



    # ###### SET UP THE PANEL ######
    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      print "building menus failed: %s" % msg


    def mkbox(label, toolbar, editor, sz_x=300, sz_y=190):
      label = gtk.Label(label)
      label.set_property('angle', 90)
      tools = merge.get_widget(toolbar)
      tools.set_property('orientation', gtk.ORIENTATION_VERTICAL)
      tools.set_property('icon-size', gtk.ICON_SIZE_MENU)
      tools.set_property('toolbar-style', gtk.TOOLBAR_ICONS)
      w = gtk.ScrolledWindow()
      w.set_size_request(-1, -1)
      w.set_shadow_type( gtk.SHADOW_ETCHED_IN )
      w.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
      w.add( editor )
      box = gtk.EventBox()
      box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16000,36000,65535))
      box.set_size_request(sz_x,sz_y)
      box.add(hpack( PArgs(vpack(tools, PArgs(label, False)), False), w))
      return box


    devbox = mkbox('Devices', '/DevToolBar', self.devcfg_editor.view )
    clkbox = mkbox('Clocks', '/ClockToolBar', self.clock_editor.view )
    sigbox = mkbox('Signal\nRoutes','/SignalToolBar',self.signal_editor['view'])
    bkdbox = mkbox('Connections', '/HostsToolBar', self.hosts['view'] )

    clk_sig_pane = gtk.VPaned()
    clk_sig_pane.pack1( clkbox )
    clk_sig_pane.pack2( sigbox )

    config = gtk.HPaned()
    config.pack1( clk_sig_pane )
    config.pack2( devbox )

    body = gtk.Notebook()
    body.set_tab_border(0)
    body.append_page( config, gtk.Label('Signals/Triggers/Devices') )
    body.append_page( bkdbox, gtk.Label('Connections') )
    body.set_tab_reorderable( config, True )

    self.vbox.pack_start( body )

    self.show_all()
    ## Close dialog on user response
    self.connect("response", lambda d, r: d.destroy())



  def create_action_group(self):
    # GtkActionEntry
    entries = (
      # SIGNAL ROUTES EDITOR
      ( 'SIG:Add', gtk.STOCK_ADD,         # name, stock id
        None, None,                       # label, accelerator
        'Add signal route after '
        'current signal route',           # tooltip
        self.activate_action ),
      ( 'SIG:Delete', gtk.STOCK_DELETE,   # name, stock id
        None, None,                       # label, accelerator
        'Delete current signal route',    # tooltip
        self.activate_action ),
      ( 'SIG:Up', gtk.STOCK_GO_UP,        # name, stock id
        None, None,                       # label, accelerator
        'Move current signal route up',   # tooltip
        self.activate_action ),
      ( 'SIG:Down', gtk.STOCK_GO_DOWN,    # name, stock id
        None, None,                       # label, accelerator
        'Move current signal route up',   # tooltip
        self.activate_action ),

      ( 'CLK:Add', gtk.STOCK_ADD,         # name, stock id
        None, None,                       # label, accelerator
        'Add clock source',               # tooltip
        self.activate_action ),
      ( 'CLK:Delete', gtk.STOCK_DELETE,   # name, stock id
        None, None,                       # label, accelerator
        'Delete current clock source',    # tooltip
        self.activate_action ),

      ( 'DEV:Add', gtk.STOCK_ADD,         # name, stock id
        None, None,                       # label, accelerator
        'Add device configuration',       # tooltip
        self.activate_action ),
      ( 'DEV:Delete', gtk.STOCK_DELETE,   # name, stock id
        None, None,                       # label, accelerator
        'Delete device configuration',    # tooltip
        self.activate_action ),

      ( 'BKD:Add', gtk.STOCK_ADD,         # name, stock id
        None, None,                       # label, accelerator
        'Add connection to host',      # tooltip
        self.activate_action ),
      ( 'BKD:Delete', gtk.STOCK_DELETE,   # name, stock id
        None, None,                       # label, accelerator
        'Delete connection to host',   # tooltip
        self.activate_action ),
    )
  
    # GtkToggleActionEntry
    toggle_entries = (
      #( 'Run', gtk.STOCK_MEDIA_PLAY,               # name, stock id
      #   '_Run', '<control>space',                 # label, accelerator
      #  'Activate waveform output',                # tooltip
      #  self.activate_action,
      #  True ),                                    # is_active
    )
  
    #     # Create the menubar and toolbar
    action_group = gtk.ActionGroup('ConfigActions')
    action_group.add_actions(entries)
    action_group.add_toggle_actions(toggle_entries)


    def delrow( action, stor, ed, delparent=False ):
      i = ed.get_selection().get_selected()[1]
      if i:
        if delparent:
          j=i
          while j:
            i=j
            j = stor.iter_parent(i)

        n = stor.iter_next( i )
        stor.remove( i )
        if n:
          ed.get_selection().select_iter( n )

    def addrow( action, stor, ed ):
      stor.insert_before( ed.get_selection().get_selected()[1] )


    def add_dev_config( action, devcfg ):
      devices = backend.get_devices()
      S = set( devices.keys() )
      configured_devices = [ D[devcfg.LABEL]  for D in devcfg ]
      L = list( S.difference( configured_devices ) )
      L.sort()
      dev = do_popup_selection( self, L )
      if not dev:
        return

      self.store.pause()
      template = devices[dev].get_config_template()
      devcfg.load( { dev : template }, clear=False )
      self.store.unpause()
      self.store.update(devcfg)


    def add_clock( action, clocks ):
      channels = backend.get_timing_channels()
      S = set( channels.keys() )
      configured_clocks = [ C[clocks.LABEL]  for C in clocks ]
      L = list( S.difference( configured_clocks ) )
      L.sort()
      clk = do_popup_selection( self, L )
      if not clk:
        return

      self.store.pause()
      template = channels[clk].get_config_template()
      clocks.load( { clk : template }, clear=False )
      self.store.unpause()
      self.store.update(clocks)


  
    # Finish off with creating references to each of the actual actions
    self.actions = {
      'SIG:Add'    : (addrow, self.store.signals, self.signal_editor['view']),
      'SIG:Delete' : (delrow, self.store.signals, self.signal_editor['view']),
      'SIG:Up'     : lambda a: sys.stderr.write('Move waveform element up\n'),
      'SIG:Down'   : lambda a: sys.stderr.write('Move waveform element down\n'),

      'CLK:Add'    : (add_clock, self.store.clocks),
      'CLK:Delete' : (delrow, self.store.clocks, self.clock_editor.view,True),

      'DEV:Add'    : (add_dev_config, self.store.devcfg),
      'DEV:Delete' : (delrow, self.store.devcfg, self.devcfg_editor.view,True),

      'BKD:Add'    : (addrow, self.store.hosts, self.hosts['view']),
      'BKD:Delete' : (delrow, self.store.hosts, self.hosts['view']),
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


class Range:
  def __init__(self, dev, cfg_path):
    self.dev = dev
    self.cfg_path = cfg_path

    cfg = self.cfg()
    self.doreload = 'doreload' in cfg and cfg['doreload']
    r = cfg['range']
    if not self.doreload:
      self.r = r

    # if range is list/tuple or callable, this entry needs a combo box
    self.combo = type(r) in [list, tuple] or ('combo' in cfg and cfg['combo'])

  def cfg(self):
    """
    Return the full config item.
    """
    return get_leaf_node( self.dev.get_config_template(), self.cfg_path )

  def __call__(self):
    """
    Return the range.
    """
    if self.doreload:
      r = self.cfg()['range']
    else:
      r = self.r
    if callable(r):
      return r()
    else:
      return r

  def is_combo(self):
    return self.combo

  def __iter__(self):
    return iter(self())

  def get_adjustment(self):
    r = self()
    if type(r) is xrange:
      return r[0], r[-1], -1, -1
    else:
      return min(r), max(r), -1, -1


class ClockRange:
  def __init__(self, terminals, clocks, signals):
    self.terminals  = terminals
    self.clocks     = clocks
    self.signals    = signals

    assert type(self.terminals()) in [list, tuple], \
      'device clocks must be lists/tuples'

  def is_combo(self):
    return True

  def __iter__(self):
    terms = self.terminals()
    return iter( accessible_clocks(terms, self.clocks, self.signals) )


def get_leaf_node( D, path ):
  if len(path) > 1:
    return get_leaf_node( D[path[0]], path[1:] )
  else:
    return D[path[0]]


class RangeFactory:
  def __init__(self, store, for_clocks):
    self.store = store
    self.for_clocks = for_clocks

  def __call__(self, path, i, model):
    if self.for_clocks:
      devs = backend.get_timing_channels()
    else:
      devs = backend.get_devices()

    r = Range( devs[path[0]], path[1:] )
    if path[1] == 'clock':
      assert model[i][model.TYPE] == str, 'expected string clock type'
      print 'I am supposed to make a clock list generator'
      return ClockRange(r, self.store.clocks, self.store.signals)
    else:
      return r



def show(win, store):
  dialog = ConfigDialog(win, store)
  return dialog.run()



def do_popup_selection( parent, choices ):
  devs = gtk.TreeStore(str,str)
  edit.helpers.add_paths_to_combobox_tree( devs, choices )
  menu_items = gtk.ComboBox( devs )
  edit.helpers.prep_combobox_for_tree( menu_items )
  menu_items.show()

  menu = gtk.Dialog('Select Channel', parent,
    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL)
  menu.set_position(position=gtk.WIN_POS_MOUSE)
  menu.set_decorated(False)
  menu.vbox.pack_start( menu_items )
  menu_items.selected_device = None

  def respond(w):
    selection = w.get_model()[w.get_active_iter()][0]
    print 'selection: ', selection
    if selection is not None:
      w.selected_device = selection
      menu.response(gtk.RESPONSE_OK)
      return True
    return False

  def cancel(w):
    menu.response(gtk.RESPONSE_CANCEL)
    return True

  menu_items.connect('changed', respond)
  menu_items.connect('popdown', cancel)

  gobject.timeout_add( 100, menu_items.popup )
  res = menu.run()
  menu.hide()
  if res != gtk.RESPONSE_OK:
    return None
  return menu_items.selected_device
