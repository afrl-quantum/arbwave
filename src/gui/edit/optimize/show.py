# vim: ts=2:sw=2:tw=80:nowrap

import gtk, gobject

import numpy as np

from ..helpers import GTVC
from ...storage.gtk_tools import get_file, NoFileError

ui_info = \
"""<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='Open'/>
      <menuitem action='Save'/>
      <menuitem action='SaveAs'/>
      <separator/>
      <menuitem action='Close'/>
    </menu>
  </menubar>
</ui>"""

class Show(gtk.Dialog):
  FILTERS = [
    ('*.txt', 'ASCII Data file (*.txt)'),
    ('*',     'All files (*)'),
  ]
  COLPREFIX = '#Columns: '

  def __init__(self, columns, title='Optimization Parameters',
               parent=None, target=None, model=False):
    actions = [
    #  gtk.STOCK_OK,     gtk.RESPONSE_OK,
    #  gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL
    ]
    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    gtk.Dialog.__init__( self, title, parent, flags, tuple(actions) )

    self.set_default_size(550, 600)
    self.set_border_width(10)

    # Set up the file menu
    merge = gtk.UIManager()
    self.set_data("ui-manager", merge)
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      print 'building menus failed: {msg}'.format(msg=msg)
    self.vbox.pack_start( merge.get_widget('/MenuBar'), False, False, 0 )

    # Set up the Body of the display
    V = self.view = gtk.TreeView()
    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,-1)
    scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    scroll.add( V )
    scroll.show_all()
    self.vbox.pack_start(scroll)

    self.set_columns( columns )

    self.filename = None


  def set_columns(self,columns):
    # clear out all current columns
    for c in self.view.get_columns():
      self.view.remove_column( c )

    # add new model and columns
    self.columns = columns
    self.params = gtk.ListStore( *([str]*(len(columns))) )
    self.view.set_model( self.params )
    for i in xrange(len(columns)):
      self.view.append_column(GTVC(columns[i], gtk.CellRendererText(), text=i))


  def add(self, *stuff):
    self.params.append( stuff )


  def get_all_data(self):
    return np.array([[ i for i in row ]  for row in self.params]).astype(float)


  def set_all_data(self, data):
    self.params.clear()
    if len(data) > 0 and len(data[0]) != len(self.columns):
      raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                          .format(n=len(self.columns)) )

    for i in data:
      self.params.append( i )


  def create_action_group(self):
    # GtkActionEntry
    entries = (
      ( 'FileMenu', None, '_File' ),               # name, stock id, label
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
      ( 'Close', gtk.STOCK_CLOSE,                   # name, stock id
        '_Close', '<control>C',                     # label, accelerator
        'Close',                                    # tooltip
        self.activate_action ),
    )

    # GtkToggleActionEntry
    toggle_entries = ()

    #     # Create the menubar and toolbar
    action_group = gtk.ActionGroup('ShowActions')
    action_group.add_actions(entries)
    action_group.add_toggle_actions(toggle_entries)

    # Finish off with creating references to each of the actual actions
    self.actions = {
      'Open'      : ( self.gtk_open_handler ),
      'Save'      : ( self.gtk_save_handler ),
      'SaveAs'    : ( self.gtk_save_handler, True),
      'Close'     : lambda a: self.destroy(),
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


  def gtk_open_handler(self, action):
    try:
      config_file = get_file(filters=Show.FILTERS)
      F = open( config_file )
    except NoFileError:
      return # this happens when get_file returns None

    firstline = F.readline()
    if firstline.startswith(Show.COLPREFIX):
      self.set_columns( firstline[len(Show.COLPREFIX):].split() )
    F.seek(0)

    try:
      data = np.loadtxt(F)
      self.set_all_data( data )
    finally:
      F.close()
    self.filename = config_file

  def gtk_save_handler(self, action, force_new=False):
    try:
      config_file = self.filename
      if (not force_new) and config_file:
        F = open( config_file, 'w' )
      else:
        config_file = get_file(False, filters=Show.FILTERS)
        F = open( config_file, 'w' )
        self.filename = config_file
    except NoFileError:
      return # this happens when get_file returns None
    F.write( Show.COLPREFIX + '\t'.join(self.columns) + '\n' )
    np.savetxt( F, self.get_all_data() )
    F.close()
