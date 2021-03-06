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

from ..tools.gui_callbacks import do_gui_operation
from ..processor import default
from .edit.helpers import GTVC, GCRT, toggle_item
from .packing import hpack, vpack, Args as PArgs, VBox
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
  types = dict(
    raw = True,
    average = False,
    error = False,
    errorOfMean = True,
  )

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
    exec('self.{l}(ax,lt)'.format(l=label))


class DataDialog(gtk.Window):
  FILTERS = [
    ('*.txt', 'ASCII Data file (*.txt)'),
    ('*',     'All files (*)'),
  ]
  COLPREFIX           = '#Columns: '
  FMTPREFIX           = '#Formats: '
  ENABLED             = '<Enabled>'
  BEGIN_SCRIPT        = '#BEGIN-SCRIPT'
  END_SCRIPT          = '#END_SCRIPT'
  DEFAULT_LINE_STYLE  = 'o, r.--, gd, kx'

  def __init__(self, columns=['Undefined'], title='Data Viewer',
               parent=None, autonamer=None, fmt='%.20g',
               globals=default.get_globals()):
    """
    autonamer:  a routine that can be passed in that provides automatic naming
      for save files.

    fmt      : Format string/array as specified by numpy.savetxt (only a single
               string or a sequence of strings are suppored for reading)
               Default:  '%.20g'
    """
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
    super(DataDialog,self).__init__( title=title, **kwargs )

    self.autonamer = autonamer
    self.fmt = fmt
    self.filename = None
    self.paused = False
    self.sigs = list() # no signal handlers by default
    self.params = None # null param table by default
    self.new_data = False
    self.default_globals = globals
    self.Globals = dict()
    self.vbox = VBox()

    # BEGIN GUI LAYOUT
    self.set_default_size(550, 600)
    self.set_border_width(10)
    super(DataDialog,self).add(self.vbox)

    # Set up the file menu
    merge = gtk.UIManager()
    self.ui_manager = merge
    merge.insert_action_group(self.create_action_group(), 0)
    self.add_accel_group(merge.get_accel_group())
    try:
      mergeid = merge.add_ui_from_string(ui_info)
    except gobject.GError as msg:
      print('building menus failed: {msg}'.format(msg=msg))
    self.vbox.pack_start( merge.get_widget('/MenuBar'), False, False, 0 )

    def set_predef(combo, entry, is_xaxis):
      i = combo.get_active()
      if i >= 1:
        data_text = 'data[:,{}]'.format(i-1)
        entry.set_text(data_text)
      else:
        data_text = entry.get_text()
        if is_xaxis and data_text == '':
          data_text = 'range( len( y_data ) )'
          entry.set_text(data_text)
      self.update_plot()

    def set_custom(entry, combo, is_xaxis):
      combo.set_active(0)
      if is_xaxis and entry.get_text() == '':
        entry.set_text( 'range( len( y_data ) )' )
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
    with self.paused_updates(False):
      set_predef( self.x_selection, self.custom_x, True)
    self.reuse = gtk.CheckButton('Re-use')
    self.reuse.set_active(True)
    self.autosave = gtk.CheckButton('AutoSave')
    self.autosave.set_active(True)
    self.autosave.set_sensitive(False)
    check_boxes = [self.reuse, self.autosave]
    if self.autonamer:
      self.autoname = gtk.CheckButton('AutoName')
      self.autoname.set_active(True)
      check_boxes += [self.autoname]
    self.line_style = gtk.Entry()
    self.line_style.set_text( self.DEFAULT_LINE_STYLE )
    self.line_style.connect('activate', self.update_plot)

    def mkCheckBox(l, default_value):
      l = l[0].upper() + l[1:]
      cb = gtk.CheckButton(label=l)
      cb.set_active(default_value)
      cb.connect( 'clicked', self.update_plot )
      return cb

    self.line_selection = {
      l:mkCheckBox(l,v)  for l,v in ComputeStats.types.items()
    }

    col_sel_box = hpack(
      vpack(
        hpack(PArgs(gtk.Label('X'),False,False,0), self.x_selection),
        self.custom_x ),
      vpack(
        hpack(PArgs(gtk.Label('Y'),False,False,0), self.y_selection),
        self.custom_y ),
      vpack(
        hpack(*check_boxes),
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

    def get_data_labels():
      """
      Get a list of names for the data columns used in the current dataset.
      """
      return [l[0] for l in self.columns]

    def get_data(include_disabled=True):
      """
      Get a fresh numpy.array representation of the data.

      include_disabled:

        False:  Function will return a new copy of the automatically
          created "data" varaible:  An array that does not include the first
          column (which represents the value of the "Enable/Disable" checkbox
          visible in the data table) and which does *not* include any data for
          which the "Enable/Disable" checkbox is not selected.

        True:  First column of the returned array will be the "Enable/Disable"
          column and every row will be included regardless of the value of the
          "Enable/Disable" checkbox.

      Note: the variable 'data' automatically holds the current array of data
      without (a) the rows that are disabled and (b) without the
      "Enable/Disable" column.
      """
      return self.get_all_data(include_disabled)

    def get_internal_data_table():
      """
      Get a handle to the actual Gtk storage (Gtk.ListStore) used to hold the
      data of the table visible on the dataviewer panel.
      """
      return self.params

    def paused_updates(update_on_finish=True):
      """
      Use with 'with' statement to temporarily pause plot updates during block
      operation.  Useful when updating many items in the internal table at once.

      Example:
        with paused_updates():
          do_some_stuff
        # upon exit, a single update will occur

        #or
        with paused_updates(False):
          do_some_stuff
        # upon exit, no updates will occur
      """
      return self.paused_updates(update_on_finish)

    def update():
      """
      Trigger a plot update and refresh of the 'data' variable that represents
      the plottable data.
      """
      self.update_plot()

    self.shell.shell_cmds += [get_data_labels,
                              get_data,
                              get_internal_data_table,
                              paused_updates,
                              update]

    self.shell.ui = self

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
    exec(self.script.representation(), self.Globals)
    self.shell.update_globals()
    self.Globals['data'] = self.get_all_data()


  def update_plot(self, *args, **kwargs):
    if not self.paused:
      self.new_data = True

  def paused_updates(self, update_on_finish=True):
    class UpdatePause(object):
      def __enter__(o_self):
        self.paused = True
        return o_self
      def __exit__(o_self, exc_type, exc_value, traceback):
        self.paused = False
        if update_on_finish:
          self.update_plot()

    return UpdatePause()


  def set_columns(self,columns):
    # clear out all current columns
    for c in self.view.get_columns():
      self.view.remove_column( c )

    # disconnect old signal handlers and delete old table
    for S in self.sigs:
      self.params.disconnect(S)
    del self.params

    # add new model and columns
    self.columns = gtk.ListStore( str )
    self.columns.append( ('',) )
    for c in columns:
      self.columns.append( (c,) )
    self.x_selection.set_model( self.columns )
    self.y_selection.set_model( self.columns )

    self.params = gtk.ListStore( bool, *([str]*(len(columns))) )
    self.sigs = [
      self.params.connect(i, self.update_plot)
      for i in ['row-changed', 'row-deleted', 'row-inserted', 'rows-reordered']
    ]
    self.view.set_model( self.params )

    r_enable = gtk.CellRendererToggle()
    r_enable.set_property( 'activatable', True )
    r_enable.connect( 'toggled', toggle_item, self.params, 0 )
    c_enable = GTVC( '?', r_enable )
    c_enable.add_attribute( r_enable, 'active', 0 )
    self.view.append_column( c_enable )
    for i in range(len(columns)):
      self.view.append_column(GTVC(columns[i], GCRT(), text=i+1))


  def add(self, *stuff):
    # ensure we have string representations
    stuff = tuple( str(i) for i in stuff )
    def do_append():
      # if it is not visible, we do not add data!
      if not self.is_drawable(): return

      self.params.append( (True,) + stuff )

      if self.autosave.get_sensitive() and self.autosave.get_active():
        self.gtk_save_handler()
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

      # update soft-copy of data
      self.Globals['data'] = self.get_all_data()

      if len(self.Globals['data']) == 0:
        return True

      L = dict()
      y_data = eval( ytxt, self.Globals, L )
      L['y_data'] = y_data
      # reorder the data with respect to x-axis
      data = sorted(zip(eval( xtxt, self.Globals, L ), y_data),
                    key = lambda i : i[0])
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
    except Exception as e:
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
    with self.paused_updates():
      fmts = self.fmt
      if type(fmts) is str:
        fmts = (self.fmt,)
      fmt = [
        '{' + fmt_i.replace('%', ':') + '}' for fmt_i in fmts
      ]

      self.params.clear()
      if has_enabled:
        if len(data) > 0 and len(data[0]) != (len(self.columns)):
          raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                              .format(n=(len(self.columns))) )
        for i in data:
          self.params.append( [i[0]] +
            [fmt[j%len(fmt)].format(ii) for j,ii in enumerate(i[1:])]
          )
      else:
        if len(data) > 0 and len(data[0]) != (len(self.columns)-1):
          raise RuntimeError( 'Cannot load data--Expected N x {n} data' \
                              .format(n=(len(self.columns)-1)) )
        for i in data:
          self.params.append( [True] +
            [fmt[j%len(fmt)].format(ii) for j,ii in enumerate(i)]
          )


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
        '_Close', '<control>W',                     # label, accelerator
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
    line = F.readline().strip()
    has_enabled = False
    if line.startswith(self.COLPREFIX):
      cols = line[len(self.COLPREFIX):].split('\t')
      if cols[0].strip() == self.ENABLED:
        cols.pop(0)
        has_enabled = True
      self.set_columns( cols )
      has_columns = True

    line = F.readline().strip()
    # set formats, if they were stored in file
    formats = None
    if line.startswith(self.FMTPREFIX):
      formats = line[len(self.FMTPREFIX):].split('\t')
      if has_enabled:
        formats = formats[1:]

      self.fmt = formats

      # prepare for next block
      line = F.readline().strip()

    # next, read in the script if supplied
    script = []
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
        # if we have already written to the file and we are not asked to create
        # a new file, write over the old version
        F = open( config_file, 'wb' )
      else:
        # if there is not a previous filename, lets attempt to create one
        get_file_kwargs = dict(doopen=False, filters=self.FILTERS)

        if self.autonamer and self.autoname.get_active():
          # the calling code requested some control over the naming
          get_file_kwargs.update(self.autonamer())

        config_file = get_file(**get_file_kwargs)
        F = open( config_file, 'wb' )
        self.filename = config_file
    except NoFileError:
      return # this happens when get_file returns None

    def Y(m,start=1):
      # yield all except the first, blank, entry
      for i in range(start,len(m)):
        yield m[i][0]

    # create formats for columns
    if type(self.fmt) is str:
      fmts = ('%d',) + (self.fmt,)*(len(self.columns) - 1)
    else:
      fmts = ('%d',) + tuple(self.fmt)

    # save column name info
    F.write(( self.COLPREFIX + self.ENABLED + '\t' + \
             '\t'.join([i for i in Y(self.columns)]) + '\n' ).encode())
    # save column format info
    F.write(( self.FMTPREFIX + '\t'.join(fmts) + '\n' ).encode())
    # save the script
    F.write(( self.BEGIN_SCRIPT + '\n#' +
             '\n#'.join( self.script.representation().strip().split('\n') ) +
             '\n' + self.END_SCRIPT + '\n' ).encode())
    # finally, save the data
    np.savetxt( F, self.get_all_data(True), fmt=fmts )
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
