#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import traceback
from gi.repository import Gtk as gtk, GObject as gobject, GLib as glib
import logging, re

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import \
  FigureCanvasGTK3Agg as FigCanvas
from matplotlib.backends.backend_gtk3 import \
  NavigationToolbar2GTK3 as NavigationToolbar

from matplotlib.mlab import find

from ..tools.gui_callbacks import do_gui_operation
from ..processor import default
from .edit.helpers import GTVC, GCRT, toggle_item
from .packing import hpack, vpack, Args as PArgs
from .storage.gtk_tools import get_file, NoFileError
from . import stores
from . import embedded

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


default_script = """\
# This script sets global variables and/or functions that are useful for
# plotting.  All other plotting scripts and processing will be done in this
# context.
from physical.unit import *
from physical.constant import *
from physical import unit
import numpy as np
from numpy import r_
"""


class ComputeStats:
  types = ['raw', 'average', 'error', 'errorOfMean']

  def __init__(self, X, Y):
    self.X = X
    self.Y = Y
    self.x, self.y0, self.y2, self.N = list(), list(), list(), list()
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
        self.N.append( N )
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
    self.N.append( N )

  def raw(self,ax,lt):
    ax.plot(self.X,self.Y,lt)

  def error(self,ax,lt):
    y0 = np.array(self.y0)
    y2 = np.array(self.y2)
    ax.errorbar( self.x, y0, yerr=(y2 - y0**2)**0.5, fmt=lt )

  def errorOfMean(self,ax,lt):
    y0 = np.array(self.y0)
    y2 = np.array(self.y2)
    N  = np.array(self.N)
    # for the error we are using standard deviation of the mean
    ax.errorbar( self.x, y0, yerr=((y2 - y0**2) / N)**0.5, fmt=lt )

  def average(self,ax,lt):
    ax.plot(self.x,self.y0,lt)

  def plot(self, label, ax, lt):
    exec 'self.{l}(ax,lt)'.format(l=label)


class DataDialog(gtk.Dialog):
  FILTERS = [
    ('*.txt', 'ASCII Data file (*.txt)'),
    ('*',     'All files (*)'),
  ]
  COLPREFIX           = '#Columns: '
  ENABLED             = '<Enabled>'
  BEGIN_SCRIPT        = '#BEGIN-SCRIPT'
  END_SCRIPT          = '#END_SCRIPT'
  DEFAULT_LINE_STYLE  = 'o, ro--, kD'

  def __init__(self, columns=['Undefined'], title='Data Viewer',
               parent=None, globals=default.get_globals()):
    kwargs = dict()
    if parent is not None:
      kwargs.update(
        parent = parent,
        actions = [
        #  gtk.STOCK_OK,     gtk.ResponseType.OK,
        #  gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL
        ],
        flags = gtk.DialogFlags.DESTROY_WITH_PARENT,
      )
    super(DataDialog,self).__init__( title, **kwargs )

    self.filename = None
    self.new_data = False
    self.default_globals = globals
    self.Globals = dict()

    # BEGIN GUI LAYOUT
    self.set_default_size(550, 600)
    self.set_border_width(10)

    # Set up the file menu
    merge = gtk.UIManager()
    self.ui_manager = merge
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError, msg:
      print 'building menus failed: {msg}'.format(msg=msg)
    self.vbox.pack_start( merge.get_widget('/MenuBar'), False, False, 0 )

    def set_predef(combo, entry, is_xaxis):
      i = combo.get_active()
      if i >= 1:
        data_text = 'data[:,{}]'.format(i-1)
        entry.set_text(data_text)
      else:
        data_text = entry.get_text()
        if is_xaxis and data_text == '':
          data_text = 'xrange( len( y_data ) )'
          entry.set_text(data_text)
      self.update_plot()

    def set_custom(entry, combo, is_xaxis):
      combo.set_active(0)
      if is_xaxis and entry.get_text() == '':
        entry.set_text( 'xrange( len( y_data ) )' )
      self.update_plot()

    def mk_xy_combo(is_xaxis, text_column=0,model=None):
      if model:
        combo = gtk.ComboBox.new_with_model(model)
      else:
        combo = gtk.ComboBox()
      cell = gtk.CellRendererText()
      combo.pack_start(cell, True )
      combo.add_attribute(cell, 'text', text_column)
      e = gtk.Entry()
      combo.connect('changed', set_predef, e, is_xaxis)
      e.connect('activate', set_custom, combo, is_xaxis)
      return combo, e

    self.x_selection, self.custom_x = mk_xy_combo(True)
    self.y_selection, self.custom_y = mk_xy_combo(False)
    set_predef( self.x_selection, self.custom_x, True)
    self.reuse = gtk.CheckButton('Re-use')
    self.reuse.set_active(True)
    self.autosave = gtk.CheckButton('Autosave')
    self.autosave.set_active(True)
    self.autosave.set_sensitive(False)
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
      vpack(
        hpack(PArgs(gtk.Label('X'),False,False,0), self.x_selection),
        self.custom_x ),
      vpack(
        hpack(PArgs(gtk.Label('Y'),False,False,0), self.y_selection),
        self.custom_y ),
      vpack(
        hpack(self.reuse, self.autosave),
        hpack(PArgs(gtk.Label('Style'),False,False,0), self.line_style) ),
    )
    col_sel_box.show_all()

    line_sel_box = hpack( *self.line_selection.values() )
    line_sel_box.show_all()

    body = gtk.VPaned()

    # Set up the Body of the display
    V = self.view = gtk.TreeView()
    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,10)
    scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    scroll.add( V )
    body.pack1(scroll, resize=True)


    self.axes, self.canvas, toolbar = init_plot(self)

    self.canvas.set_size_request(-1,50)
    body.pack2( vpack( PArgs(toolbar,False,False,0), self.canvas ) )

    body.show_all()

    self.shell = embedded.Python(
      get_globals=lambda : self.Globals,
      reset = self.exec_script,
    )

    self.script = stores.Script(
      default_script,
      title='Variables/Functions...',
      changed=self.exec_script,
    )

    # pack the rest in
    viewer = vpack(
      PArgs( col_sel_box, False, False, 0 ),
      PArgs( line_sel_box, False, False, 0 ),
      body,
    )

    self.notebook = gtk.Notebook()
    self.notebook.set_property('border-width',0)
    self.notebook.append_page(viewer, gtk.Label('Data Viewer'))
    self.notebook.set_tab_reorderable( viewer, True )

    shell_sb = gtk.ScrolledWindow()
    shell_sb.add(self.shell)
    self.notebook.append_page(shell_sb, gtk.Label('Shell'))
    self.notebook.set_tab_reorderable( shell_sb, True )

    self.script.edit(notebook=self.notebook, keep_open=True)

    def tab_tear( notebook, page, x, y ):
      notebook.remove_page( notebook.page_num(page) )
      if hasattr(page, 'orig_parent'):
        w = page.orig_parent
      else:
        w = gtk.Window()
      w.add( page )
      w.show()

    self.notebook.connect('create-window', tab_tear)

    self.vbox.pack_start( self.notebook, True, True, 0 )
    glib.timeout_add(1, self.notebook.set_current_page, 0)


    # ### DONE WITH GUI LAYOUT ###
    self.set_columns( columns )
    self.exec_script()
    # schedule the plotter
    glib.timeout_add( 100, self.plot_data )
    self.connect('destroy', lambda e: gtk.main_quit())


  def exec_script(self, *a):
    self.Globals.clear()
    self.Globals.update( self.default_globals )
    exec self.script.representation() in self.Globals
    self.shell.update_globals()
    self.Globals['data'] = self.get_all_data()


  def update_plot(self, *args, **kwargs):
    self.new_data = True


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

    self.params = gtk.ListStore( bool, *([str]*(len(columns))) )
    self.view.set_model( self.params )

    def TI( c, p, m, i ):
      toggle_item( c, p, m, i )
      self.update_plot()

    r_enable = gtk.CellRendererToggle()
    r_enable.set_property( 'activatable', True )
    r_enable.connect( 'toggled', TI, self.params, 0 )
    c_enable = GTVC( '?', r_enable )
    c_enable.add_attribute( r_enable, 'active', 0 )
    self.view.append_column( c_enable )
    for i in xrange(len(columns)):
      self.view.append_column(GTVC(columns[i], GCRT(), text=i+1))


  def add(self, *stuff):
    # ensure we have string representations
    stuff = tuple( str(i) for i in stuff )
    def do_append():
      # if it is not visible, we do not add data!
      if not self.is_drawable(): return

      self.params.append( (True,) + stuff )

      if 'data' in self.Globals:
        # only append the current new
        new_row = [self.convert_row_data(stuff)]
        D = self.Globals['data']
        if len(D) == 0:
          self.Globals['data'] = np.array(new_row, dtype=float)
        else:
          self.Globals['data'] = np.append(D, new_row, axis=0)
      else:
        # generate the missing data...
        self.Globals['data'] = self.get_all_data()

      if self.autosave.get_sensitive() and self.autosave.get_active():
        self.gtk_save_handler()
      self.new_data = True
    do_gui_operation( do_append )


  def plot_data(self):
    if not self.is_drawable():
      return False

    if not self.new_data:
      return True

    try:
      self.new_data = False

      def get_col( combo, entry ):
        i = combo.get_active()
        data_text = entry.get_text()
        if i >= 1:
          return data_text, self.columns[i][0]
        else:
          label = entry.get_text()
          pat = 'data\s*\[\s*:\s*,\s*{}\s*]'
          for i in re.findall(pat.format('([0-9]*)'), label):
            label = re.sub(pat.format(i), self.columns[int(i)+1][0], label)
          # now we'll attempt to clean up the label a bit
          return data_text, label

      xtxt, x_label = get_col( self.x_selection, self.custom_x )
      ytxt, y_label = get_col( self.y_selection, self.custom_y )
      line_style = self.line_style.get_text()
      if not line_style:
        line_style = self.DEFAULT_LINE_STYLE
      line_style = [ i.strip() for i in line_style.split(',') ]

      if ytxt == '':
        self.axes.clear()
        self.canvas.draw()
        return True # nothing to plot, clear plot and return

      if 'data' not in self.Globals:
        # in case the user deleted it(?)
        self.Globals['data'] = self.get_all_data()

      if len(self.Globals['data']) == 0:
        return True

      L = dict()
      y_data = eval( ytxt, self.Globals, L )
      L['y_data'] = y_data
      data = zip( eval( xtxt, self.Globals, L ), y_data )
      # reorder the data with respect to x-axis
      data.sort( key = lambda i : i[0] )
      x_data = np.array([ i[0] for i in data ], dtype=float)
      y_data = np.array([ i[1] for i in data ], dtype=float)

      self.axes.clear()

      good = np.argwhere( np.isfinite(y_data) )
      stats = ComputeStats(x_data[good].flatten(), y_data[good].flatten())
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
    except Exception, e:
      traceback.print_exc()
      logging.debug( 'dataviewer: %s', e )
    return True


  def convert_row_data(self, row):
    return [ eval(str(col),self.Globals) for col in row ]

  def get_all_data(self, include_disabled=False):
    if include_disabled:
      return np.array([
        self.convert_row_data(row) for row in self.params
      ], dtype=float)
    else:
      return np.array([
        self.convert_row_data(row[1:]) for row in self.params if row[0]
      ], dtype=float)


  def set_all_data(self, data, has_enabled=False):
    self.params.clear()
    if has_enabled:
      if len(data) > 0 and len(data[0]) != (len(self.columns)):
        raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                            .format(n=(len(self.columns))) )
      for i in data:
        self.params.append( [i[0]] + [str(ii) for ii in i[1:]] )
    else:
      if len(data) > 0 and len(data[0]) != (len(self.columns)-1):
        raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                            .format(n=(len(self.columns)-1)) )
      for i in data:
        self.params.append( [True] + [str(ii) for ii in i] )
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


  def gtk_open_handler(self, action=None):
    try:
      config_file = get_file(filters=self.FILTERS)
      F = open( config_file )
    except NoFileError:
      return # this happens when get_file returns None

    # first work out column labels if supplied
    line = F.readline()
    has_enabled = False
    if line.startswith(self.COLPREFIX):
      cols = line[len(self.COLPREFIX):].split('\t')
      if cols[0].strip() == self.ENABLED:
        cols.pop(0)
        has_enabled = True
      self.set_columns( cols )
      has_columns = True

    # next, read in the script if supplied
    script = []
    line = F.readline().strip()
    if line == self.BEGIN_SCRIPT:
      line = F.readline()
      while line.strip() != self.END_SCRIPT:
        assert line[0] == '#', 'Expected # at beginning of stored script line'
        script.append(line[1:])
        line = F.readline()

    # start file back at zero and use numpy to load the data
    F.seek(0)
    try:
      data = np.loadtxt(F)
    finally:
      F.close()

    if not has_columns:
      self.set_columns(['unknown'] * data.shape[1])
    self.set_all_data( data, has_enabled )

    if script:
      self.script.set_text( ''.join(script) )
    else:
      self.script.set_text( default_script )

    self.filename = config_file
    self.autosave.set_sensitive(False)

  def gtk_save_handler(self, action=None, force_new=False):
    try:
      config_file = self.filename
      if (not force_new) and config_file:
        F = open( config_file, 'w' )
      else:
        config_file = get_file(False, filters=self.FILTERS)
        F = open( config_file, 'w' )
        self.filename = config_file
    except NoFileError:
      return # this happens when get_file returns None

    def Y(m,start=1):
      # yield all except the first, blank, entry
      for i in xrange(start,len(m)):
        yield m[i][0]

    # save column info
    F.write( self.COLPREFIX + self.ENABLED + '\t' + \
             '\t'.join([i for i in Y(self.columns)]) + '\n' )
    # save the script
    F.write( self.BEGIN_SCRIPT + '\n#' +
             '\n#'.join( self.script.representation().strip().split('\n') ) +
             '\n' + self.END_SCRIPT + '\n' )
    # finally, save the data
    np.savetxt( F, self.get_all_data(True) )
    F.close()
    self.autosave.set_sensitive(True)


def init_plot(win):
  dpi = 100
  #  class matplotlib.figure.Figure(figsize=None,
  #                                 dpi=None, facecolor=None,
  #                                 edgecolor=None, linewidth=1.0,
  #                                 frameon=True, subplotpars=None)
  fig = Figure(figsize=(3.0, 3.0), dpi=dpi)
  canvas = FigCanvas(fig)
  axes = fig.add_subplot(111, label='generic', navigate=True)
  toolbar = NavigationToolbar( canvas, win )

  return axes, canvas, toolbar
