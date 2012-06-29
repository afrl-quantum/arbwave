# vim: ts=2:sw=2:tw=80:nowrap
import gtk, gobject

from matplotlib.figure import Figure

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas

# or NavigationToolbar for classic
#from matplotlib.backends.backend_gtk import NavigationToolbar2GTK as NavigationToolbar
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

import pylab

import numpy as np
from scipy.interpolate import UnivariateSpline

from helpers import *
import spreadsheet


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


    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    if model:
      flags |= gtk.DIALOG_MODAL

    gtk.Dialog.__init__( self, title, parent, flags )

    self.set_default_size(550, 600)
    self.set_border_width(10)


    self.pause_update = False

    V = self.view = gtk.TreeView()
    V.set_property( 'rules-hint', True )
    V.get_selection().set_mode( gtk.SELECTION_MULTIPLE )

    self.sheet_cb = spreadsheet.Callbacks( V, ('', '') )
    self.sheet_cb.connect('clean',
      lambda: self.set_pause(True), lambda: self.set_pause(False) )

    self.renderers = R = {
      'x' : gtk.CellRendererText(),
      'y' : gtk.CellRendererText(),
    }

    R['x'].set_property( 'editable', True )
    R['y'].set_property( 'editable', True )

    C = {
      'x' : GTVC( 'Voltage (V)',  R['x'],  text=Editor.X ),
      'y' : GTVC( 'Output (V)',   R['y'],  text=Editor.Y ),
    }

    V.append_column( C['x'] )
    V.append_column( C['y'] )

    V.set_size_request( 200, 100 )

    # create the scrolled window for the spreadsheet
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.set_shadow_type(gtk.SHADOW_IN)
    sw.add( V )

    # Create the plotting canvas
    f = Figure(figsize=(5,4), dpi=100)
    self.axes = f.add_subplot(111)
    self.canvas = FigureCanvas(f)  # a gtk.DrawingArea
    self.canvas.set_size_request(300,100)
    toolbar = NavigationToolbar(self.canvas, self)

    self.channel_select = gtk.ComboBox(channels)
    cbr = gtk.CellRendererText()
    self.channel_select.clear()
    self.channel_select.pack_start( cbr )
    self.channel_select.add_attribute( cbr, 'text', channels.LABEL )
    self.channel_select.connect('changed',
      lambda c: self._set_channel(c.get_active_text())
    )
    # This ensures you can't select digital channels
    def is_sensitive(celllayout, cell, model, i, *user_args):
      if model[i][model.DEVICE].startswith('Digital'):
        cell.set_property('sensitive', False)
        cell.set_property('visible', False)
      else:
        cell.set_property('sensitive', True)
        cell.set_property('visible', True)
    self.channel_select.set_cell_data_func( cbr, is_sensitive )

    self.units = gtk.Entry()
    def update_units_label(entry):
      # just a simple test to see if the units evaluate
      eval(self.units.get_text(), self.get_globals())

      C['y'].set_title( 'Output ({})'.format(entry.get_text()))
      self.axes.set_ylabel('Output ({})'.format(self.units.get_text()))
      self.canvas.draw()
      T = self.units.get_text()
      if self.chan and self.chan[self.channels.UNITS] != T:
        self.chan[self.channels.UNITS] = T

    self.units.connect('activate', update_units_label)
    self.units.set_text('V')


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


    ubox = gtk.HBox()
    ubox.pack_start( self.channel_select )
    ubox.pack_start( gtk.Label('Output Scale/Units:  ') )
    ubox.pack_start( self.units )

    pbox = gtk.HBox()
    pbox.pack_start( gtk.Label('Interpolation:      Order:' ) )
    pbox.pack_start( self.order )
    pbox.pack_start( gtk.Label('Smoothing:' ) )
    pbox.pack_start( self.smoothing )

    bottom = gtk.VBox()
    bottom.pack_start(ubox, False, False)
    bottom.pack_start(pbox, False, False)
    bottom.pack_start(sw)

    body = gtk.VPaned()
    body.pack1( self.canvas, True )
    body.pack2( bottom, True )
    self.vbox.pack_start( toolbar, False, False )
    self.vbox.pack_start( body )
    self.show_all()

    # default to first channel
    self.set_channel()


  def set_channel(self, label=None):
    """Determines the new channel and sets it"""
    if not ( self.channels and len(self.channels) ):
      return

    if label == None:
      return
    if label != self.channel_select.get_active_text():
      for i in xrange(len(self.channels)):
        if label == self.channels[i][self.channels.LABEL]:
          self.channel_select.set_active(i)
          # we rely on the channel_select callback to finish this
          return
      raise KeyError('Could not determine channel')


  def _set_channel(self, label):
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
    for chan in self.channels:
      if chan[self.channels.LABEL] == label:
        break
    if chan[self.channels.SCALING] is None:
      chan[self.channels.SCALING] = gtk.ListStore(str,str)
    if not chan[self.channels.UNITS]:
      chan[self.channels.UNITS] = 'V'
    if chan[self.channels.INTERP_ORDER] < 1:
      chan[self.channels.INTERP_ORDER] = 1
    # INTERP_SMOOTHING defaults to zero already

    self.units.set_text( chan[self.channels.UNITS] )
    self.order.set_value( chan[self.channels.INTERP_ORDER] )
    self.smoothing.set_value( chan[self.channels.INTERP_SMOOTHING] )
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

    self.units.activate()

    D = dict()
    for x,y in self.chan[self.channels.SCALING]:
      if x and y:
        yval = eval(y,self.get_globals())
        assert 'units' not in dir(yval), 'expected unitless scaler'
        D[eval(x,self.get_globals())] = yval
    # make sure that the order of data is correct
    D = D.items()
    D.sort(key=lambda v: v[0]) # sort by x
    D = np.array(D)

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
  "import physical\n" \
  "from physical import unit\n" \
  "from physical.unit import *\n" \
  "from physical.constant import *\n"
  Globals = dict()
  exec Global_script in Globals

  class Channels(gtk.ListStore):
    LABEL            = 0
    UNITS            = 1
    SCALING          = 2
    INTERP_ORDER     = 3
    INTERP_SMOOTHING = 4
    DEVICE           = 5
    def __init__(self):
      gtk.ListStore.__init__(self, str, str, gtk.ListStore, int, float, str)

  channels = Channels()
  channels.append(( 'MOT Detuning', 'MHz', gtk.ListStore(str,str), 1, 0, 'Analog' ))
  channels.append(( 'MOT Power', 'mW', gtk.ListStore(str,str), 1, 0, 'Analog' ))
  edit(channels, globals=Globals)

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))

