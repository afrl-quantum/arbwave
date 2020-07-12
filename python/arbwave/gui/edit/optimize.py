# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, Gdk as gdk

from ...processor.executor.optimize import Make as executor_optimize_make
from ...processor.executor.optimize.algorithms import algorithms

import sys, re, pydoc
from logging import warning, debug, info, error

from ...tools.print_units import M
from .. import stores
from ..packing import *
from .. import dataviewer as viewers
from . import generic
from . import helpers
from .helpers import GTVC, GCRT
from .spreadsheet import keys


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
  gdk.drag_status(ctx, gdk.DragAction.COPY, time)

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
      exec('global ' + name)
    if eval(name,Globals) == eval(new_item,Globals) and \
       model[path][model.VALUE] == new_item:
      return
    exec('{n} = {v}'.format(n=name, v=new_item), Globals)
    model[path][model.VALUE] = new_item
  except:
    return



def query_alg_tooltip(widget, x, y, keyboard_tip, tooltip):
  is_row, x, y, algs, path, iter = widget.get_tooltip_context(x, y, keyboard_tip)
  if not is_row:
    return False

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

    self.repetitions = gtk.SpinButton.new(
      gtk.Adjustment(lower=1, upper=sys.maxsize, step_incr=1, page_incr=5),
      1,
      10,
    )
    self.vbox.pack_start(
      hpack(gtk.Label('Number of Repetitions'), self.repetitions),
      True, True, 0
    )
    if 'repetitions' in settings:
      self.repetitions.set_value( settings['repetitions'] )

    body = gtk.VPaned()
    self.vbox.pack_start( body, True, True, 0 )


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
          ( p['name'], repr(M(eval(p['name'],Globals))),
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
    vbox.pack_start( V, True, True, 0 )


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
    V.connect('drag-motion', drag_motion)
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

    vbox.pack_start( V, True, True, 0 )


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

  def __call__(self, runnable, Globals):
    S = self.settings.get(self.run_label, dict())
    S = optimize_dialog(self.win, settings=S, Globals=Globals)

    if S:
      self.settings[self.run_label] = S
      return executor_optimize_make(S, viewers.db)(runnable, Globals)
    else:
      class Cancelled:
        def onstart(OSelf): pass
        def onstop(OSelf): pass
        def run(OSelf): pass

      return Cancelled()


def optimize_dialog(parent, Globals, settings, cache_tolerance=1e-3):
  opt = OptimView(settings, Globals, parent=parent)
  try:
    if opt.run() not in [ gtk.ResponseType.OK ]:
      return None
  finally:
    opt.hide()

  parameters = list()
  for p in opt.params:
    parameters.append(
      { 'name'  : p[opt.params.NAME],
        'min'   : p[opt.params.MIN],
        'max'   : p[opt.params.MAX],
        'scale' : p[opt.params.SCALE],
        'enable': p[opt.params.ENABLE],
      }
    )

  EQ = Constraints.EQ
  EN = Constraints.ENABLE
  constraints = {c[EQ]:c[EN] for c in opt.constraints}

  return {
    'algorithms' : opt.algs.representation(),
    'parameters' : parameters,
    'constraints': constraints,
    'repetitions': opt.repetitions.get_value_as_int(),
  }
