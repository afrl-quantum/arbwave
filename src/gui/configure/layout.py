# vim: ts=2:sw=2:tw=80:nowrap

import gtk, sys
import gobject

from ..packing import Args as PArgs, VBox, hpack, vpack
from .. import edit

ui_info = \
'''<ui>
  <toolbar  name='SignalToolBar'>
    <toolitem action='SIG:Add'/>
    <toolitem action='SIG:Delete'/>
    <separator/>
    <toolitem action='SIG:Up'/>
    <toolitem action='SIG:Down'/>
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


    # ###### SET UP THE PANEL ######
    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      print "building menus failed: %s" % msg


    siglabel = gtk.Label('Signal\nRoutes')
    siglabel.set_property('angle', 90)
    sigtools = merge.get_widget('/SignalToolBar')
    sigtools.set_property('orientation', gtk.ORIENTATION_VERTICAL)
    sigtools.set_property('icon-size', gtk.ICON_SIZE_MENU)
    sigtools.set_property('toolbar-style', gtk.TOOLBAR_ICONS)
    sigbox = gtk.EventBox()
    sigbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(16000,36000,65535))
    sigbox.set_size_request(300,190)
    sigbox.add( hpack(
      PArgs( vpack(sigtools, PArgs(siglabel,False)), False ),
      self.signal_editor['view']
    ))
    self.vbox.pack_start(sigbox)

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


    def delrow( action, stor, ed ):
      i = ed.get_selection().get_selected()[1]
      n = stor.iter_next( i )
      stor.remove( i )
      if n:
        ed.get_selection().select_iter( n )

    def addrow( action, stor, ed ):
      stor.insert_before( ed.get_selection().get_selected()[1] )

  
    # Finish off with creating references to each of the actual actions
    self.actions = {
      'SIG:Add'    : (addrow, self.store.signals, self.signal_editor['view']),
      'SIG:Delete' : (delrow, self.store.signals, self.signal_editor['view']),
      'SIG:Up'     : lambda: sys.stderr.write('Move waveform element up\n'),
      'SIG:Down'   : lambda: sys.stderr.write('Move waveform element down\n'),
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

