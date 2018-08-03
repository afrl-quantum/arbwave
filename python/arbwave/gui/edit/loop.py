# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, Gdk as gdk

import sys, re, pydoc

import numpy as np
from matplotlib import mlab

from ...tools.print_units import M

from . import helpers
from .helpers import GTVC, GCRT

from .. import dataviewer as viewers
from .spreadsheet import keys

nan = float('nan')

class Parameters(gtk.TreeStore):
  NAME    = 0
  ITERABLE= 1
  ISGLOBAL= 2
  ENABLE  = 3

  DEFAULT = ('i', 'range(0,10,2)', False, True)

  def __init__(self):
    super(Parameters,self).__init__(
      str, #name
      str, #iterable
      bool,#global
      bool,#enable
    )

  def list_recursive(self, iter):
    L = list()
    for i in iter:
      F = dict()
      F['name']     = i[ Parameters.NAME ]
      F['iterable'] = i[ Parameters.ITERABLE ]
      F['isglobal'] = i[ Parameters.ISGLOBAL ]
      F['enable']   = i[ Parameters.ENABLE ]

      if self.iter_has_child( i.iter ):
        F['children'] = self.list_recursive( i.iterchildren() )
      L.append( F )
    return L

  def list(self):
    return self.list_recursive( iter(self) )

  def representation(self):
    return self.list()

  def load_recursive(self, L, parent=None):
    for i in L:
      me=self.append(parent,(i['name'],i['iterable'],i['isglobal'],i['enable']))
      if 'children' in i:
        self.load_recursive( i['children'], me )

  def load(self,L):
    self.clear()
    self.load_recursive(L)



def drag_motion(w, ctx, x, y, time):
  mask = w.get_window().get_pointer()[2]
  if mask & gdk.ModifierType.CONTROL_MASK:
    gdk.drag_status( ctx, gdk.DragAction.COPY, time )


class LoopView(gtk.Dialog):
  def __init__(self, settings, Globals, title='Loop Parameters',
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

    super(LoopView,self).__init__( title, parent, flags, tuple(actions) )

    self.set_default_size(750, 600)
    self.set_border_width(10)


    self.params = Parameters()
    if 'parameters' in settings:
      self.params.load( settings['parameters'] )
    else:
      self.params.append( None, Parameters.DEFAULT )

    V = self.view = gtk.TreeView( self.params )
    V.set_reorderable(True)
    #V.connect('drag-begin', begin_drag, self.window)
    #V.connect('drag-end', end_drag, self.window, waveforms)
    V.connect('drag-motion', drag_motion)
    V.connect('key-press-event', self.view_keypress_cb)
    R = {
      'name'    : GCRT(),
      'iterable': GCRT(),
      'isglobal': gtk.CellRendererToggle(),
      'enable'  : gtk.CellRendererToggle(),
    }
    R['name'].set_property( 'editable', True )
    R['name'].connect('edited', helpers.set_item, self.params, Parameters.NAME)
    R['iterable'].set_property( 'editable', True )
    R['iterable'].connect( 'edited', helpers.set_item, self.params, Parameters.ITERABLE)
    R['isglobal'].set_property( 'activatable', True )
    R['isglobal'].connect('toggled', helpers.toggle_item, self.params, Parameters.ISGLOBAL)
    R['enable'].set_property( 'activatable', True )
    R['enable'].connect('toggled', helpers.toggle_item, self.params, Parameters.ENABLE)

    C = {
      'name'    : GTVC('Variable', R['name'], text=Parameters.NAME),
      'iterable': GTVC('Iterable', R['iterable'], text=Parameters.ITERABLE),
      'isglobal': GTVC('Global', R['isglobal']),
      'enable'  : GTVC('Enable', R['enable']),
    }
    C['isglobal'].add_attribute(R['isglobal'], 'active', Parameters.ISGLOBAL)
    C['enable'].add_attribute(R['enable'], 'active', Parameters.ENABLE)
    V.append_column( C['name'] )
    V.append_column( C['iterable'] )
    V.append_column( C['isglobal'] )
    V.append_column( C['enable'] )

    V.show()

    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,-1)
    scroll.set_shadow_type(gtk.ShadowType.ETCHED_IN)
    scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
    scroll.add( V )
    scroll.show()
    self.vbox.pack_start( scroll, True, True, 0 )


  def view_keypress_cb(self, entry, event):
    if event.keyval == keys.INSERT:
      model, rows = self.view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      if rows:
        rows = [ model.get_iter(p)  for p in rows ]
        for row in rows:
          p = model[row].parent and model[row].parent.iter
          model.insert_before( p, row, Parameters.DEFAULT )
      else:
        model.append( None, Parameters.DEFAULT )
      return True
    elif event.keyval == keys.DEL:
      model, rows = self.view.get_selection().get_selected_rows()
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
  def __init__(self, parent, runnable, Globals, settings):
    self.runnable = runnable
    self.Globals = Globals

    self.show = None

    loop = LoopView(settings, Globals, parent=parent)
    self.cancelled = False
    try:
      if loop.run() not in [ gtk.ResponseType.OK ]:
        print('cancelled!')
        self.cancelled = True
        return
    finally:
      loop.hide()

    self.parameters = loop.params.representation()
    V = self.get_columns( self.parameters )
    self.variables = dict()
    for i in range(len(V)):
      if V[i][0] in self.variables: continue # don't overwrite
      self.variables[ V[i][0] ] = { 'order':i, 'value':nan, 'isglobal':V[i][1] }
    # now get sorted unique list of variables
    V = sorted(self.variables.items(), key = lambda v: v[1]['order'])

    self.show = viewers.db.get(
      columns=([ vi[0] for vi in V] \
              + ['Merit'] + self.runnable.extra_data_labels()),
      title='Loop Parameters/Results',
    )


  def get_settings(self):
    if self.cancelled: return None
    return {
      'parameters' : self.parameters,
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
        self._for_loop_main()

    if self.cancelled: return Cancelled()
    else:              return ORun()


  def _for_loop_main(self):
    self.show.show()
    Locals = dict()
    for f in self.parameters:
      if f['enable']:
        self._for_loop(f, Locals)

  def _for_loop(self, p, Locals):
    assert p['enable'], 'for loop should be enabled here!'
    if p['isglobal'] and not re.search('["\'\[(\.]', p['name']):
      exec('global ' + p['name'])

    iterable = eval( p['iterable'], self.Globals, Locals )
    for xi in iterable:
      if p['isglobal']:
        exec('{n} = {xi}'.format(n=p['name'], xi=M(xi)), self.Globals)
      else:
        Locals[ p['name'] ] = xi
        self.variables[ p['name'] ]['value'] = xi # global values reread below

      if 'children' in p:
        for child in p['children']:
          if child['enable']:
            self._for_loop(child, Locals)
      else:
        self._do_run()

      # this variable is now out of scope...!
      if not p['isglobal']:
        Locals.pop( p['name'] )
        self.variables[ p['name'] ]['value'] = nan

  def _do_run(self):
    def L(r):
      # need better test like "if iterable"
      if r is None:
        return [0]
      elif type(r) in [ np.ndarray, list, tuple ]:
        return list(r)
      else:
        return [r]

    # We update the globals here to make sure they are all set correctly,
    # regardless of whether we are currently in a loop that changes them.
    for vi in self.variables.items():
      if vi[1]['isglobal']: vi[1]['value'] = eval(vi[0], self.Globals)
    results = sorted(self.variables.values(), key = lambda v : v['order'])
    results = [ v['value'] for v in results ] + L( self.runnable.run() )
    self.show.add( *M(results) )


  def get_columns(self, parameters):
    """
    Returns a list of (column names, isglobal) for each parameter in order of
    operation of the for loops.
    """
    L = list()
    for p in parameters:
      if not p['enable']: continue
      L.append( (p['name'], p['isglobal']) )
      L += self.get_columns( p.get('children', list()) )
    return L


main_settings = dict()

def main():
  import traceback, pprint
  from .optimize import test
  e = Make(None, 'func', main_settings)( test.func(), test.get_globals() )

  print('e: ', e)
  return e
