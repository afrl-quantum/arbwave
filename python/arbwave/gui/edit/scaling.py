# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk, GObject as gobject
import re

from matplotlib.figure import Figure

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk3 import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
#from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTKCairo as FigureCanvas

# or NavigationToolbar for classic
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
#from matplotlib.backends.backend_gtk3agg import NavigationToolbar2GTK3Agg as NavigationToolbar

import pylab

import numpy as np
from scipy.interpolate import UnivariateSpline

from helpers import *
import spreadsheet

def fstr(num):
  return '{:.12g}'.format(num)


class NumberEntryEnforcer(object):
  expr     =      '^[0-9]*\.?[0-9]*([eE][-+]?[0-9]*)?$'
  all_expr = '^[-+]?[0-9]*\.?[0-9]*([eE][-+]?[0-9]*)?$'

  def __init__(self, editor, column, allow_negative=False):
    self.old = ''
    self.editor = editor
    self.column = column
    if allow_negative:
      self.expr = self.all_expr
  def __call__(self, entry):
    val = entry.get_text()
    if not re.match(self.expr, val):
      entry.set_text(self.old)
    else:
      self.old = val

  def activate(self, entry):
    val = entry.get_text()
    try:
      val = float(val)
      if self.editor.chan:
        self.editor.chan[self.column] = val
      entry.set_text(fstr(val))
    except:
      if self.editor.chan:
        val = fstr(self.editor.chan[self.column])
        entry.set_text(val)
      else:
        entry.set_text(self.old)


class Editor(gtk.Dialog):
  X = 0
  Y = 1

  def get_globals(self):
    if self.globals_src:
      return self.globals_src()
    return self.globals


  def __init__( self, channels, title='Edit Scaling',
                parent=None, target=None, model=False,
                add_undo=None, globals_src=None, globals=globals()):
    self.add_undo = add_undo
    self.channels = channels
    self.globals_src = None
    if globals_src:
      assert callable(globals_src), 'expected callable globals_src'
      self.globals_src = globals_src
    self.globals = globals

    self.handlers = dict()
    self.chan = None


    flags = gtk.DialogFlags.DESTROY_WITH_PARENT
    if model:
      flags |= gtk.DialogFlags.MODAL

    super(Editor,self).__init__( title, parent, flags )

    self.set_default_size(550, 600)
    self.set_border_width(10)


    self.pause_update = False

    V = self.view = gtk.TreeView()
    V.set_property( 'rules-hint', True )
    V.get_selection().set_mode( gtk.SelectionMode.MULTIPLE )

    self.sheet_cb = spreadsheet.Callbacks( V, ('', '') )
    self.sheet_cb.connect('clean',
      lambda: self.set_pause(True), lambda: self.set_pause(False) )

    self.renderers = R = {
      'x' : GCRT(),
      'y' : GCRT(),
    }

    R['x'].set_property( 'editable', True )
    R['y'].set_property( 'editable', True )

    C = {
      'x' : GTVC( 'Voltage (V)',  R['x'],  text=Editor.X ),
      'y' : GTVC( 'Output (V)',   R['y'],  text=Editor.Y ),
    }

    V.append_column( C['x'] )
    V.append_column( C['y'] )
    self.C = C

    V.set_size_request( 200, 100 )

    # create the scrolled window for the spreadsheet
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    sw.set_shadow_type(gtk.ShadowType.IN)
    sw.add( V )

    # Create the plotting canvas
    f = Figure(figsize=(5,4), dpi=100)
    self.axes = f.add_subplot(111)
    self.canvas = FigureCanvas(f)  # a gtk.DrawingArea
    self.canvas.set_size_request(300,100)
    toolbar = NavigationToolbar(self.canvas, self)
    self.plot_offset_label = gtk.Label('Plot Offset [V]:')

    self.channel_select = gtk.ComboBox.new_with_model(channels)
    cbr = gtk.CellRendererText()
    self.channel_select.clear()
    self.channel_select.pack_start( cbr, True )
    self.channel_select.add_attribute( cbr, 'text', channels.LABEL )
    self.channel_select.connect('changed',
      lambda c: self._set_channel(self.channels[c.get_active()])
    )
    # This ensures you can't select digital channels
    def is_sensitive(celllayout, cell, model, i, *user_args):
      if model[i][model.DEVICE].lower().startswith('digital/'):
        cell.set_property('sensitive', False)
        cell.set_property('visible', False)
      else:
        cell.set_property('sensitive', True)
        cell.set_property('visible', True)
    self.channel_select.set_cell_data_func( cbr, is_sensitive )

    self.units = gtk.Entry()
    self.units.set_width_chars(8)
    def update_units_label(entry):
      T = self.units.get_text()
      # just a simple test to see if the units evaluate
      eval(T, self.get_globals())

      C['y'].set_title( 'Output ({})'.format(T) )
      self.axes.set_ylabel( 'Output ({})'.format(T) )
      self.canvas.draw()
      if self.chan and self.chan[self.channels.UNITS] != T:
        self.chan[self.channels.UNITS] = T
        self.update_plot()

    self.units.connect('activate', update_units_label)
    self.units.set_text('V')

    self.offset = gtk.Entry()
    self.offset.set_width_chars(10)
    def update_offset(entry):
      T = self.offset.get_text()
      # just a simple test to see if the units evaluate
      if not T:
        T = None
      elif T.partition('#')[0].strip():
        eval(T, self.get_globals())

      if self.chan and self.chan[self.channels.OFFSET] != T:
        self.chan[self.channels.OFFSET] = T
        self.update_plot()
    self.offset.connect('activate', update_offset)


    self.order = gtk.SpinButton()
    self.order.set_range(1,5)
    self.order.set_increments(1,2)
    def update_order(entry):
      if self.chan:
        self.chan[self.channels.INTERP_ORDER] = self.order.get_value_as_int()
        self.update_plot()

    self.order.connect('value-changed', update_order)
    self.order.set_value(1)


    self.smoothing = gtk.SpinButton(digits=3)
    self.smoothing.set_range(0,10000000)
    self.smoothing.set_increments(0.5,1)
    def update_smoothing(entry):
      if self.chan:
        self.chan[self.channels.INTERP_SMOOTHING] = self.smoothing.get_value()
        self.update_plot()

    self.smoothing.connect('value-changed', update_smoothing)
    self.smoothing.set_value(0)


    self.enforce_scale_offset = \
      NumberEntryEnforcer(self, self.channels.PLOT_SCALE_OFFSET, True)
    self.scale_offset = gtk.Entry()
    self.scale_offset.set_text('0.0')
    self.scale_offset.set_width_chars(15)
    self.scale_offset.connect('changed', self.enforce_scale_offset)
    self.scale_offset.connect('activate', self.enforce_scale_offset.activate)
    self.scale_offset.set_tooltip_text(
      'Specify an offset for the waveform plot')

    self.enforce_scale_factor = \
      NumberEntryEnforcer(self, self.channels.PLOT_SCALE_FACTOR)
    self.scale_factor = gtk.Entry()
    self.scale_factor.set_text('1.0')
    self.scale_factor.set_width_chars(15)
    self.scale_factor.connect('changed', self.enforce_scale_factor)
    self.scale_factor.connect('activate', self.enforce_scale_factor.activate)
    self.scale_factor.set_tooltip_text(
      'Specify a scaling factor for the waveform plot')


    ubox = gtk.HBox()
    ubox.pack_start( self.channel_select, True, True, 0 )
    ubox.pack_start( gtk.Label('Output Scale/Units:  '), True, True, 0 )
    ubox.pack_start( self.units, True, True, 0 )

    pbox = gtk.HBox()
    pbox.pack_start( gtk.Label('Interpolation:      Order:' ), True, True, 0 )
    pbox.pack_start( self.order, True, True, 0 )
    pbox.pack_start( gtk.Label('Smoothing:' ), True, True, 0 )
    pbox.pack_start( self.smoothing, True, True, 0 )

    obox = gtk.HBox()
    obox.pack_start( gtk.Label('Output Offset/Units:'), True, True, 0 )
    obox.pack_start( self.offset, True, True, 0 )

    sbox = gtk.HBox()
    sbox.pack_start( self.plot_offset_label, True, True, 0 )
    sbox.pack_start( self.scale_offset, True, True, 0 )
    sbox.pack_start( gtk.Label('Plot Scale:'), True, True, 0 )
    sbox.pack_start( self.scale_factor, True, True, 0 )

    bottom = gtk.VBox()
    bottom.pack_start(ubox, False, False, 0)
    bottom.pack_start(pbox, False, False, 0)
    bottom.pack_start(obox, False, False, 0)
    bottom.pack_start(sbox, False, False, 0)
    bottom.pack_start(sw, True, True, 0)

    body = gtk.VPaned()
    body.pack1( self.canvas, True )
    body.pack2( bottom, True )
    self.vbox.pack_start( toolbar, False, False, 0 )
    self.vbox.pack_start( body, True, True, 0 )
    self.show_all()

    # default to first channel
    self.set_channel()


  def set_channel(self, label=None):
    """Determines the new channel and sets it"""
    if not ( self.channels and len(self.channels) ):
      return

    if label == None:
      return
    if label != self.channels[self.channel_select.get_active()]:
      for i in xrange(len(self.channels)):
        if label == self.channels[i][self.channels.LABEL]:
          self.channel_select.set_active(i)
          # we rely on the channel_select callback to finish this
          return
      raise KeyError('Could not determine channel')


  def _set_channel(self, chan):
    #disconnect handlers from old model
    if self.chan:
      for i in self.handlers['store']:
        self.chan[self.channels.SCALING].disconnect(i)

      for i in self.handlers['x']:
        self.renderers['x'].disconnect(i)

      for i in self.handlers['y']:
        self.renderers['y'].disconnect(i)

    if not ( self.channels and len(self.channels) ):
      return

    self.set_pause(True)

    self.chan = None
    self.view.set_model( None )

    # set new model
    if chan[self.channels.SCALING] is None:
      chan[self.channels.SCALING] = gtk.ListStore(str,str)
    if not chan[self.channels.UNITS]:
      chan[self.channels.UNITS] = 'V'
    if chan[self.channels.INTERP_ORDER] < 1:
      chan[self.channels.INTERP_ORDER] = 1

    devname = chan[self.channels.DEVICE].lower()
    if   devname.startswith('analog/'):
      self.C['x'].set_title( 'Voltage (V)' )
      self.plot_offset_label.set_text('Plot Offset [V]:')
    elif devname.startswith('dds/'):
      self.C['x'].set_title( 'Frequency (Hz)' )
      self.plot_offset_label.set_text('Plot Offset [Hz]:')
    # INTERP_SMOOTHING defaults to zero already

    self.units.set_text( chan[self.channels.UNITS] )
    self.units.activate()
    self.offset.set_text( chan[self.channels.OFFSET] or '' )
    self.order.set_value( chan[self.channels.INTERP_ORDER] )
    self.smoothing.set_value( chan[self.channels.INTERP_SMOOTHING] )
    self.scale_offset.set_text( fstr(chan[self.channels.PLOT_SCALE_OFFSET]) )
    self.scale_factor.set_text( fstr(chan[self.channels.PLOT_SCALE_FACTOR]) )
    store = chan[self.channels.SCALING]
    self.view.set_model( store )


    #connect handlers to new model
    self.handlers['store'] = [
      store.connect('row-changed',  lambda m,p,i: self.update_plot()),
      store.connect('row-deleted',  lambda m,p: self.update_plot()),
      store.connect('row-inserted', lambda m,p,i: self.update_plot()),
    ]

    self.handlers['x'] = self.sheet_cb.connect_column( self.renderers['x'],
      setitem=(set_item, store, Editor.X, self.add_undo, True) )

    self.handlers['y'] = self.sheet_cb.connect_column( self.renderers['y'],
      setitem=(set_item, store, Editor.Y, self.add_undo) )

    self.chan = chan
    self.set_pause(False)
    # clear the plot entirely first to avoid keeping a plot with no data-table
    self.axes.clear()
    self.canvas.draw()
    self.update_plot()



  def plot(self, *args, **kwargs):
    """Send the data to matplotlib"""
    self.axes.hold(False)
    self.axes.plot(*args, **kwargs)
    pylab.setp(self.axes.get_xticklabels(), fontsize=8)
    pylab.setp(self.axes.get_yticklabels(), fontsize=8)
    self.axes.grid(True)
    self.axes.set_xlabel('Voltage (V)')
    self.axes.set_ylabel('Output ({})'.format(self.units.get_text()))
    self.canvas.draw()


  def set_pause(self,arg):
    """Do not send to plotter just because a signal handler was called"""
    self.pause_update = bool(arg)


  def update_plot(self):
    if self.pause_update:
      return

    D = calculate(self.chan[self.channels.SCALING],
                  self.chan[self.channels.UNITS],
                  self.chan[self.channels.OFFSET],
                  self.get_globals()               )

    if len(D):
      if len(D) > 1:
        s = UnivariateSpline(D[:,0], D[:,1],
          k=self.order.get_value_as_int(),
          s=self.smoothing.get_value(),
        )
        xs = np.linspace(D[0,0],D[-1,0], 100*len(D))
        self.plot( D[:,0], D[:,1], 'o', xs, s(xs) )
      else:
        self.plot( D[:,0], D[:,1], 'o' )


  # def insert_row(self):
  #   i = self.channels.insert_before(self.view.get_selection().get_selected()[1])
  #   self.add_undo( ListUndo(i, self.channels) )

  # def delete_row(self):
  #   i = self.view.get_selection().get_selected()[1]
  #   if i:
  #     n = self.channels.iter_next( i )
  #     self.add_undo( ListUndo(i, self.channels, deletion=True) )
  #     self.channels.remove( i )
  #     if n:
  #       self.view.get_selection().select_iter( n )


class ListUndo:
  def __init__(self, iter, model, deletion=False):
    self.model = model
    self.path = model.get_path( iter )
    self.position = self.path[0]
    self.new_row = list(model[iter])
    self.deletion = deletion

  def delete(self):
    self.model.remove( self.model.get_iter(self.path) )

  def insert(self):
    self.model.insert( self.position, self.new_row )

  def redo(self):
    if self.deletion: self.delete()
    else:             self.insert()

  def undo(self):
    if self.deletion: self.insert()
    else:             self.delete()



def evalIfNeeded( s, G, L=dict() ):
  if type(s) is str:
    try:
      return eval( s, G, L )
    except Exception, e:
      raise RuntimeError('Could not evaluate python text: "{}"\n{}'.format(s,e))
  else:
    return s


def calculate( scaling, units, offset, globals, return_range=False ):
  U = evalIfNeeded(units, globals)

  # we allow the user to comment out the offset (instead of just clearing it)
  if offset is not None:
    offset = offset.partition('#')[0].strip()

  # now with commented portion ignored, calculate the offset
  if offset:
    offset = evalIfNeeded(offset, globals)
    # ensure proper units
    U.unitsMatch( offset, 'Scaling offset must have proper units' )
    offset /= U
  else:
    offset = 0

  D = dict()
  for x,y in scaling:
    if x and y:
      yval = evalIfNeeded(y,globals)
      xval = evalIfNeeded(x,globals)

      try: # assume iterable first
        assert len(xval) == len(yval), \
          'Sequence entries X and Y must have same length'
        XVALS = xval
        YVALS = yval
      except TypeError: #make these into an array
        XVALS = [xval]
        YVALS = [yval]

      for xi, yi in zip( XVALS, YVALS ):
        assert 'units' not in dir(xi), \
          'expected unitless scaler in voltage entries'
        assert 'units' not in dir(yi), \
          'expected unitless scaler in output entries'
        D[xi] = float(yi - offset)

  if return_range:
    XVALS = D.keys()
    return min(XVALS), max(XVALS)

  # make sure that the order of data is correct
  D = D.items()
  D.sort(key=lambda v: v[0]) # sort by x
  D = np.array(D)
  return D



def edit(channels, title='Edit Scaling', parent=None, globals=globals()):
  ed = Editor( channels=channels,
               title=title, parent=parent,
               model=False, ### whether it should be a model dialog
               globals=globals )
  try:
    ed.run()
  finally:
    ed.destroy()


def main(argv):
  Global_script = \
"""
import physical
from physical import unit
from physical.unit import *
from physical.constant import *
import numpy as np

data = np.array([
  [0, 0],
  [1, 1.1],
  [2, 1.2],
  [3, 1.3],
  [4, 1.4],
])
"""

  Globals = dict()
  exec Global_script in Globals

  class Channels(gtk.ListStore):
    LABEL            = 0
    UNITS            = 1
    SCALING          = 2
    INTERP_ORDER     = 3
    INTERP_SMOOTHING = 4
    OFFSET           = 5
    PLOT_SCALE_OFFSET= 6
    PLOT_SCALE_FACTOR= 7
    DEVICE           = 8
    def __init__(self):
      super(Channels,self).__init__(
        str, str, gtk.ListStore, int, float, str, float, float, str
      )

  channels = Channels()
  channels.append(( 'MOT Detuning', 'MHz', gtk.ListStore(str,str), 1, 0, '', 0.0, 1.0, 'Analog' ))
  channels.append(( 'MOT Power', 'mW', gtk.ListStore(str,str), 1, 0, '10*mW', 0.0, 0.5, 'Analog' ))
  edit(channels, globals=Globals)

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

