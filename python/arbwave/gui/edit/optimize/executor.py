# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, Gdk as gdk

import sys, re, pydoc

import numpy as np
from matplotlib import mlab

import physical

from ....tools.print_units import M
from ... import stores
from ...packing import *
from ...dataviewer import DataViewer
from .. import generic
from .. import helpers
from ..helpers import GTVC, GCRT
from ..spreadsheet import keys

from algorithms import algorithms

FMAX = sys.float_info.max

class Parameters(gtk.ListStore):
  NAME = 0
  VALUE = 1
  MIN = 2
  MAX = 3
  SCALE = 4
  ENABLE = 5

  DEFAULT = ('', '', '0.0', '1.0', '1.0', True)

  def __init__(self):
    super(Parameters,self).__init__(
      str, #name
      str, #value
      str, #min
      str, #max
      str, #scale
      bool,#enable
    )


class Constraints(gtk.ListStore):
  EQ = 0
  ENABLE = 1

  DEFAULT = ('', True)

  def __init__(self):
    super(Constraints,self).__init__(
      str, #constraint
      bool,#enable
    )


def drag_motion(w, ctx, x, y, time):
  mask = w.get_window().get_pointer()[2]
  if mask & gdk.ModifierType.CONTROL_MASK:
    gdk.drag_status( ctx, gdk.DragAction.COPY, time )

def set_item_name( cell, path, new_item, model, Globals, typ=str ):
  """
    if unique is True, this searches through the immediate chlidren for
      duplicate names before allowing the edit.
  """
  new_item = typ(new_item)

  if model[path][model.NAME] == new_item:
    return  # avoid triggering a change if there is not actually a change
  model[path][model.NAME] = new_item
  try: model[path][model.VALUE] = M(eval(new_item,Globals))
  except: model[path][model.VALUE] = ''

def set_item_value( cell, path, new_item, model, Globals, typ=str ):
  """
    if unique is True, this searches through the immediate chlidren for
      duplicate names before allowing the edit.
  """
  new_item = typ(new_item)

  # first, search for corresponding global variable.  Only updates for valid
  # variables will be allowed
  # Also avoid triggering a change if there is not actually a change
  name = model[path][model.NAME]
  if not name:
    return
  try:
    if not re.search('["\'\[]', name):
      exec 'global ' + name
    if eval(name,Globals) == eval(new_item,Globals) and \
       model[path][model.VALUE] == new_item:
      return
    exec '{n} = {v}'.format(n=name, v=new_item) in Globals
    model[path][model.VALUE] = new_item
  except:
    return



def query_alg_tooltip(widget, x, y, keyboard_tip, tooltip):
  try:
    algs, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
    iter = algs.get_iter( path[0:1] ) # only consider root for alg
    alg, = algs.get(iter, algs.LABEL)

    td = pydoc.TextDoc()
    markup = td.docroutine( algorithms[alg]['actual_func'] )
    markup = ''.join(re.split('\x08.',markup))
    markup = '\n'.join(markup.split('\n')[0:20])
    markup += '\n...\n<b>For more, see scipy.optimize</b>'
    tooltip.set_markup( markup )
    widget.set_tooltip_row(tooltip, path)

    return True
  except:
    return False


class OptimView(gtk.Dialog):
  def __init__(self, settings, Globals, title='Optimization Parameters',
               parent=None, target=None, modal=False):
    actions = [
      gtk.STOCK_OK,     gtk.ResponseType.OK,
      gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL,
    ]
    flags = gtk.DialogFlags.DESTROY_WITH_PARENT
    if modal:
      flags |= gtk.DialogFlags.MODAL
      actions.pop(2)
      actions.pop(2)

    super(OptimView,self).__init__( title, parent, flags, tuple(actions) )

    self.set_default_size(550, 600)
    self.set_border_width(10)

    self.repetitions = gtk.SpinButton(
      gtk.Adjustment(lower=1, upper=sys.maxint, step_incr=1, page_incr=5)
    )
    self.vbox.pack_start(
      hpack(gtk.Label('Number of Repetitions'), self.repetitions) )
    if 'repetitions' in settings:
      self.repetitions.set_value( settings['repetitions'] )

    body = gtk.VPaned()
    self.vbox.pack_start( body )


    self.algs = stores.Generic(use_enable=True,keep_order=True)
    if 'algorithms' in settings:
      self.algs.load( settings['algorithms'] )
    else:
      self.algs.load( algorithms )
    GV = generic.Generic(
      self.algs, reorderable=True,
      range_factory=generic.RangeFactory(algorithms,use_enable=True) )
    GV.view.set_property( 'has_tooltip', True )
    GV.view.connect('query-tooltip', query_alg_tooltip)
    GV.view.get_selection().connect('changed', lambda s,V: V.trigger_tooltip_query(), GV.view)

    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,250)
    scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    scroll.add( GV.view )
    body.pack1(scroll)


    self.params = Parameters()
    if 'parameters' in settings:
      for p in settings['parameters']:
        self.params.append(
          ( p['name'], M(eval(p['name'],Globals)),
            p['min'], p['max'], p['scale'], p['enable'] )
        )
    else:
      self.params.append( Parameters.DEFAULT )

    V = gtk.TreeView( self.params )
    V.set_reorderable(True)
    #V.connect('drag-begin', begin_drag, self.window)
    #V.connect('drag-end', end_drag, self.window, waveforms)
    V.connect('drag-motion', drag_motion)
    V.connect('key-press-event', self.view_keypress_cb, V, Parameters.DEFAULT)
    R = {
      'name'  : GCRT(),
      'value' : GCRT(),
      'min'   : GCRT(),
      'max'   : GCRT(),
      'scale' : GCRT(),
      'enable'  : gtk.CellRendererToggle(),
    }
    R['name'].set_property( 'editable', True )
    R['name'].connect( 'edited', set_item_name, self.params, Globals )
    R['value'].set_property( 'editable', True )
    R['value'].connect( 'edited', set_item_value, self.params, Globals )
    R['min'].set_property( 'editable', True )
    R['min'].connect( 'edited', helpers.set_item, self.params, Parameters.MIN )
    R['max'].set_property( 'editable', True )
    R['max'].connect( 'edited', helpers.set_item, self.params, Parameters.MAX )
    R['scale'].set_property( 'editable', True )
    R['scale'].connect( 'edited', helpers.set_item, self.params, Parameters.SCALE )
    R['enable'].set_property( 'activatable', True )
    R['enable'].connect('toggled', helpers.toggle_item, self.params, Parameters.ENABLE)

    C = {
      'name' : GTVC('Variable', R['name'], text=Parameters.NAME),
      'value' : GTVC('Value', R['value'], text=Parameters.VALUE),
      'min' : GTVC('Min', R['min'], text=Parameters.MIN),
      'max' : GTVC('Max', R['max'], text=Parameters.MAX),
      'scale' : GTVC('Scale', R['scale'], text=Parameters.SCALE),
      'enable' : GTVC('Enable', R['enable']),
    }
    C['enable'].add_attribute(R['enable'], 'active', Parameters.ENABLE)
    V.append_column( C['name'] )
    V.append_column( C['value'] )
    V.append_column( C['min'] )
    V.append_column( C['max'] )
    V.append_column( C['scale'] )
    V.append_column( C['enable'] )


    vbox = VBox()
    vbox.pack_start( V )


    self.constraints = Constraints()
    if 'constraints' in settings:
      for c in settings['constraints']:
        self.constraints.append( (c,settings['constraints'][c]) )
    else:
      self.constraints.append( Constraints.DEFAULT )

    V = gtk.TreeView( self.constraints )
    V.set_reorderable(True)
    #V.connect('drag-begin', begin_drag, self.window)
    #V.connect('drag-end', end_drag, self.window, waveforms)
    V.connect('drag-motion', drag_motion, self.window)
    V.connect('key-press-event', self.view_keypress_cb, V, Constraints.DEFAULT)
    R = {
      'constraint' : GCRT(),
      'enable'  : gtk.CellRendererToggle(),
    }
    R['constraint'].set_property( 'editable', True )
    R['constraint'].connect( 'edited', helpers.set_item, self.constraints, 0)
    R['enable'].set_property( 'activatable', True )
    R['enable'].connect('toggled', helpers.toggle_item, self.constraints, Constraints.ENABLE)
    C = {
      'constraint' : GTVC('Constraint Equations', R['constraint'], text=0),
      'enable' : GTVC('Enable', R['enable']),
    }
    C['enable'].add_attribute(R['enable'], 'active', Constraints.ENABLE)
    V.append_column( C['constraint'] )
    V.append_column( C['enable'] )

    vbox.pack_start( V )


    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,250)
    scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    scroll.add_with_viewport( vbox )
    body.pack2(scroll)

    self.show_all()


  def view_keypress_cb(self, entry, event, view, DEFAULT):
    if event.keyval == keys.INSERT:
      model, rows = view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      if rows:
        rows = [ model.get_iter(p)  for p in rows ]
        for row in rows:
          model.insert_before( row, DEFAULT )
      else:
        model.append( DEFAULT )
      return True
    elif event.keyval == keys.DEL:
      model, rows = view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      rows = [ gtk.TreeRowReference(model, p)  for p in rows ]
      for r in rows:
        model.remove( model.get_iter( r.get_path() ) )
      return True
    return False



class Make:
  def __init__(self, win, run_label, settings):
    self.win = win
    self.run_label = run_label
    self.settings = settings

  def __call__(self, *args, **kwargs):
    S = self.settings.get(self.run_label,dict())
    e = Executor( self.win, settings=S, *args, **kwargs )
    S = e.get_settings()
    if S:
      self.settings[self.run_label] = S
    return e()

class Executor:
  def __init__(self, parent, runnable, Globals, settings, cache_tolerance=1e-3):
    self.runnable = runnable
    self.Globals = Globals

    self._cache = None
    self.results = dict()
    self.cache_tolerance = cache_tolerance
    self.show = None
    self.pnames = None
    self.skipped_evals = 0

    opt = OptimView(settings, Globals, parent=parent)
    self.cancelled = False
    try:
      if opt.run() not in [ gtk.ResponseType.OK ]:
        print 'cancelled!'
        self.cancelled = True
        return
    finally:
      opt.hide()

    old_pnames = self.pnames
    self.pnames = list()
    self.params = list()
    self.parameters = list()
    for p in opt.params:
      if p[opt.params.ENABLE]:
        self.pnames.append( p[opt.params.NAME] )
        self.params.append( (
          M(eval(p[opt.params.NAME],Globals)),
          M(eval(p[opt.params.MIN],Globals)),
          M(eval(p[opt.params.MAX],Globals)),
          M(eval(p[opt.params.SCALE],Globals)),
        ) )
      self.parameters.append(
        { 'name'  : p[opt.params.NAME],
          'min'   : p[opt.params.MIN],
          'max'   : p[opt.params.MAX],
          'scale' : p[opt.params.SCALE],
          'enable': p[opt.params.ENABLE],
        }
      )

    self.params = np.array( self.params )

    self.constraints = list()
    EQ = Constraints.EQ
    for c in opt.constraints:
      if c[EQ]:
        self.constraints.append( [c[EQ], lambda G : eval(c[EQ], G), Constraints.ENABLE] )

    if old_pnames is None or old_pnames != self.pnames:
      self.show = DataViewer(
        columns=(self.pnames+['Merit']+self.runnable.extra_data_labels()),
        parent=parent, globals=Globals,
      )

    algs = opt.algs
    self.alg_settings = opt.algs.representation()
    self.algorithms = {
      alg[algs.LABEL] :
        {
          arg[algs.LABEL] :
            arg[  algs.to_index[ arg[algs.TYPE] ]  ]
          for arg in alg.iterchildren()  if arg[algs.ENABLE]
        }
      for alg in algs  if alg[algs.ENABLE]
    }

    self.repetitions = opt.repetitions.get_value_as_int()

  def get_settings(self):
    if self.cancelled: return None
    return {
      'algorithms' : self.alg_settings,
      'parameters' : self.parameters,
      'constraints': { c[0]:c[2] for c in self.constraints },
      'repetitions': self.repetitions,
    }


  def __call__(self):
    class Cancelled:
      def onstart(OSelf): pass
      def onstop(OSelf): pass
      def run(OSelf): pass

    class ORun:
      def onstart(OSelf):
        self.runnable.onstart()

      def onstop(OSelf):
        self.runnable.onstop()

      def run(OSelf):
        self.show.show()
        x0 = self.params[:,0]
        scale = self.params[:,3]
        # first unscale all parameters
        x0 /= scale
        for alg in self.algorithms.items():
          self.evals = 0
          x0, merit = algorithms[alg[0]]['func'](self._call_func, x0, **alg[1])
          # print parameters rescaled
          print 'After', alg[0], 'x0: ', x0*scale, ', merit: ', merit
          print 'Number function evaluations: ', self.evals

        self.save_globals( x0 * scale )

        return True

    if self.cancelled: return Cancelled()
    else:              return ORun()


  def save_globals(self, x):
    # only try to make global variables that are fundamental types
    # (str,int,float, ...)
    globalize = [ i for i in self.pnames if not re.search('["\'\[]', i) ]
    if globalize:
      exec 'global ' + ','.join( globalize )
    for i in xrange(len(x)):
      exec '{n} = {v}'.format(n=self.pnames[i], v=M(x[i])) in self.Globals


  def _call_func(self, x):
    # before using x, ensure that it is rescaled
    x = x * self.params[:,3] # dont multiply in-place

    cached = self.lookup(x)
    if cached is not None:
      self.show.add( *M(list(x) + list(cached)) )
      self.skipped_evals += 1
      # the zeroth element of cached is the merit
      return cached[0]

    self.save_globals(x)

    # now, test constraints before running the function
    c_failed = [ True  for c in self.constraints
                  if c[2] and not c[1](self.Globals) ]
    if c_failed:
      print 'constraint failed'
      result = [FMAX] + [0]*len(self.runnable.extra_data_labels())
    else:
      def A(r):
        # need better test like "if iterable"
        if type(r) in [ np.ndarray, list, tuple ]:
          return np.array(r)
        else:
          return np.array([r])

      self.evals += 1
      # average result for the given number of repetitions
      result = sum([A(self.runnable.run()) for i in xrange(self.repetitions)]) \
             / float(self.repetitions)
      # result is necessarily a numpy array by now
      self.show.add( *M(list(x) + list(result)) )
    self.cache( x, result )

    # the zeroth element of result is supposed to be the merit
    return result[0]


  def lookup(self, x):
    if self._cache is None:
      return None

    TINY = list()
    for xi in x:
      if type(xi) is physical.Quantity:
        TINY.append( physical.Quantity(1e-30,xi.units) )
      else:
        TINY.append( 1e-30 )

    cols = self._cache.shape[1]
    found = mlab.find( abs( (
        (self._cache - x) / ( self._cache + TINY )
      ).dot(np.ones(cols)) ) < self.cache_tolerance )

    if len( found ) == 0:
      return None

    # if there are for some reason more, ignore them
    return self.results[ tuple( self._cache[ found[0] ] ) ]

  def cache(self, x, result):
    if self._cache is None:
      self._cache = np.array( [x] )
      self.results[ tuple(x) ] = result

    elif self.lookup(x) is None:
      self._cache = np.append( self._cache, [x], 0 )
      self.results[ tuple(x) ] = result
