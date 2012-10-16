# vim: ts=2:sw=2:tw=80:nowrap

import gtk, gobject

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkagg import \
  FigureCanvasGTKAgg as FigCanvas
from matplotlib.backends.backend_gtkagg import \
  NavigationToolbar2GTKAgg as NavigationToolbar

from ..helpers import GTVC
from ...packing import hpack, vpack, Args as PArgs
from ...storage.gtk_tools import get_file, NoFileError
from ....tools.gui_callbacks import do_gui_operation

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


class ComputeStats:
  types = ['raw', 'average', 'error']

  def __init__(self, X, Y):
    self.X = X
    self.Y = Y
    self.x, self.y0, self.y2 = list(), list(), list()
    if len(X)==0 or len(X) != len(Y):
      return
    N = 0.0
    I = 0
    xi = X[0]
    y0 = y2 = 0.0
    while I < len(X):
      if xi != X[I]:
        self.x.append( xi )
        self.y0.append( y0/N )
        self.y2.append( y2/N )
        N = 0.0
        xi = X[I]
        y0 = y2 = 0.0
      else:
        y0 += Y[I]
        y2 += Y[I]**2
        N += 1.0
        I += 1
    self.x.append( xi )
    self.y0.append( y0 / N )
    self.y2.append( y2 / N )

  def raw(self,ax,lt):
    ax.plot(self.X,self.Y,lt)

  def error(self,ax,lt):
    y0 = np.array(self.y0)
    y2 = np.array(self.y2)
    ax.errorbar( self.x, y0, yerr=((y2 - y0**2)**0.5), fmt=lt )

  def average(self,ax,lt):
    ax.plot(self.x,self.y0,lt)

  def plot(self, label, ax, lt):
    exec 'self.{l}(ax,lt)'.format(l=label)


DEFAULT_DATA_FUNCDTION = 'raw'

class Show(gtk.Dialog):
  FILTERS = [
    ('*.txt', 'ASCII Data file (*.txt)'),
    ('*',     'All files (*)'),
  ]
  COLPREFIX = '#Columns: '
  DEFAULT_LINE_STYLE = 'o, ro--, kD'

  def __init__(self, columns, title='Optimization Parameters/Results',
               parent=None, model=False, globals=globals()):
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

    def mk_simple_combo(text_column=0,model=None):
      combo = gtk.ComboBox(model)
      cell = gtk.CellRendererText()
      combo.pack_start(cell, True)
      combo.add_attribute(cell, 'text', text_column)
      combo.connect('changed', self.update_plot)
      return combo

    self.x_selection = mk_simple_combo()
    self.y_selection = mk_simple_combo()
    self.line_style = gtk.Entry()
    self.line_style.set_text( self.DEFAULT_LINE_STYLE )
    self.line_style.connect('activate', self.update_plot)

    def mkCheckBox(l):
      l = l[0].upper() + l[1:]
      cb = gtk.CheckButton(label=l)
      cb.connect( 'clicked', self.update_plot )
      cb.set_active(True)
      return cb

    self.line_selection = { l:mkCheckBox(l)  for l in ComputeStats.types }

    col_sel_box = hpack(
        PArgs(gtk.Label('X'),False,False,0), self.x_selection,
        PArgs(gtk.Label('Y'),False,False,0), self.y_selection,
        PArgs(gtk.Label('Style'),False,False,0), self.line_style,
    )
    col_sel_box.show_all()
    self.vbox.pack_start( col_sel_box, False, False, 0 )

    line_sel_box = hpack( *self.line_selection.values() )
    line_sel_box.show_all()
    self.vbox.pack_start( line_sel_box, False, False, 0 )

    body = gtk.VPaned()
    self.vbox.pack_start(body)

    # Set up the Body of the display
    V = self.view = gtk.TreeView()
    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,400)
    scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    scroll.add( V )
    body.pack1(scroll)


    self.axes, self.canvas, toolbar = init_plot(self)

    self.canvas.set_size_request(-1,150)
    body.pack2( vpack( PArgs(toolbar,False,False,0), self.canvas ) )

    body.show_all()
    self.set_columns( columns )

    self.filename = None
    self.new_data = False
    self.Globals = globals


  def update_plot(self, *args, **kwargs):
    self.new_data = True


  def show(self):
    def do_show():
      gobject.idle_add( self.plot_data )
      gtk.Dialog.show(self)
    do_gui_operation( do_show )


  def set_columns(self,columns):
    # clear out all current columns
    for c in self.view.get_columns():
      self.view.remove_column( c )

    # add new model and columns
    self.columns = gtk.ListStore( str )
    self.columns.append( ('',) )
    for c in columns:
      self.columns.append( (c,) )
    self.x_selection.set_model( self.columns )
    self.y_selection.set_model( self.columns )

    self.params = gtk.ListStore( *([str]*(len(columns))) )
    self.view.set_model( self.params )
    for i in xrange(len(columns)):
      self.view.append_column(GTVC(columns[i], gtk.CellRendererText(), text=i))


  def add(self, *stuff):
    def do_append():
      self.params.append( stuff )
      self.new_data = True
    do_gui_operation( do_append )


  def plot_data(self):
    if not self.is_drawable():
      return False

    if not self.new_data:
      return True

    try:
      self.new_data = False

      def get_col( combo ):
        i = combo.get_active()
        if i >= 1:
          return i-1, self.columns[i][0]
        else:
          return -1, ''

      xi, x_label = get_col( self.x_selection )
      yi, y_label = get_col( self.y_selection )
      line_style = self.line_style.get_text()
      if not line_style:
        line_style = self.DEFAULT_LINE_STYLE
      line_style = [ i.strip() for i in line_style.split(',') ]

      if yi == -1:
        self.axes.clear()
        self.canvas.draw()
        return True # nothing to plot, clear plot and return

      data = self.get_all_data()
      # reorder the data with respect to x-axis
      if data.shape[1] == 1 or xi == -1:
        # we'll just prepend an index column
        data = np.append(np.transpose([xrange(0,data.shape[0])]), data, axis=1)
        xi = 0
        yi += 1
      else:
        data.view(','.join(['f8']*data.shape[1])).sort(order='f'+str(xi),axis=0)
      self.axes.clear()

      stats = ComputeStats(data[:,xi], data[:,yi])
      i = -1
      for l,cb in self.line_selection.items():
        i += 1
        if not cb.get_active(): continue
        stats.plot(l, self.axes, line_style[i % len(line_style)])

      mn, mx = min(stats.X), max(stats.X)
      dx = mx - mn
      self.axes.set_xlim(mn - .1*dx, mx + .1*dx)
      self.axes.set_xlabel(x_label)
      self.axes.set_ylabel(y_label)
      self.canvas.draw()
    except: pass
    return True


  def get_all_data(self):
    return np.array([
      [ eval(i,self.Globals) for i in row ] for row in self.params
    ]).astype(float)


  def set_all_data(self, data):
    self.params.clear()
    if len(data) > 0 and len(data[0]) != (len(self.columns)-1):
      raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                          .format(n=(len(self.columns)-1)) )
    for i in data:
      self.params.append( i )
    self.new_data = True


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
      self.set_columns( firstline[len(Show.COLPREFIX):].split('\t') )
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

    def Y(m,start=1):
      # yield all except the first, blank, entry
      for i in xrange(start,len(m)):
        yield m[i][0]

    F.write( Show.COLPREFIX + '\t'.join([i for i in Y(self.columns)]) + '\n' )
    np.savetxt( F, self.get_all_data() )
    F.close()


def init_plot(win):
  dpi = 100
  #  class matplotlib.figure.Figure(figsize=None,
  #                                 dpi=None, facecolor=None,
  #                                 edgecolor=None, linewidth=1.0,
  #                                 frameon=True, subplotpars=None)
  fig = Figure(figsize=(3.0, 3.0), dpi=dpi)
  canvas = FigCanvas(fig)
  rect = [.1, .01, .88, .85 ]
  axes = fig.add_axes( rect, label='generic', navigate=True )
  toolbar = NavigationToolbar( canvas, win )

  return axes, canvas, toolbar
