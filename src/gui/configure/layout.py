# vim: ts=2:sw=2:tw=80:nowrap

import gtk, sys
import gobject

from ..packing import Args as PArgs, VBox, hpack, vpack
from .. import edit
from ... import backend

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
    self.devcfg_editor = edit.Generic(store.devcfg)
    self.clock_editor = edit.Generic(store.clocks)


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

    clk_sig_pane = gtk.VPaned()
    clk_sig_pane.pack1( clkbox )
    clk_sig_pane.pack2( sigbox )

    body = gtk.HPaned()
    body.pack1( devbox )
    body.pack2( clk_sig_pane )

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
      if 'clock' in template:
        template['clock']['range'] = \
          clock_list_generator(template['clock']['range'],
                               self.store.clocks,
                               self.store.signals)

      devcfg.load( { dev : template }, clear=False )

      self.store.unpause()
      self.store.update()


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
      self.store.update()


  
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


def show(win, store):
  dialog = ConfigDialog(win, store)
  return dialog.run()



def do_popup_selection( parent, choices ):
  devs = gtk.ListStore(str)
  for i in choices:
    devs.append( (i,) )
  menu_items = gtk.TreeView( devs )
  menu_items.insert_column_with_attributes(0, 'Available',
    gtk.CellRendererText(), text=0)
  menu_items.show()
  menu_items.set_hover_selection(True)

  menu = gtk.Dialog('Select Channel', parent,
    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL)
  menu.set_position(position=gtk.WIN_POS_MOUSE)
  menu.set_decorated(False)
  menu.vbox.pack_start( menu_items )
  menu_items.selected_device = None

  def respond(w,event):
    selection = menu_items.get_selection().get_selected()[1]
    if selection is not None:
      menu_items.selected_device = selection
      menu.response(gtk.RESPONSE_OK)
      return True
    return False

  menu_items.connect('button-release-event', respond)

  res = menu.run()
  menu.hide()
  if res != gtk.RESPONSE_OK:
    return None
  return devs[menu_items.selected_device][0]



class clock_list_generator:
  def __init__(self, direct, clocks, routes ):
    self.direct = direct
    self.clocks = clocks
    self.routes = routes

  def __call__(self):
    # TODO:  return a subset of clocks for which each of the direct signals are
    # connected via the routes to the subset of clocks
    return self.direct
