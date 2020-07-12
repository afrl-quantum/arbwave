# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk, Gdk as gdk

from ...processor.executor.loop import Make as executor_loop_make

from . import helpers
from .helpers import GTVC, GCRT

from .. import dataviewer as viewers
from .spreadsheet import keys

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
  gdk.drag_status(ctx, gdk.DragAction.COPY, time)


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

  def __call__(self, runnable, Globals):
    S = self.settings.get(self.run_label, dict())
    S = loop_dialog(self.win, settings=S, Globals=Globals)

    if S:
      self.settings[self.run_label] = S
      return executor_loop_make(S, viewers.db)(runnable, Globals)
    else:
      class Cancelled:
        def onstart(OSelf): pass
        def onstop(OSelf): pass
        def run(OSelf): pass

      return Cancelled()

def loop_dialog(parent, settings, Globals):
  loop = LoopView(settings, Globals, parent=parent)
  try:
    if loop.run() not in [ gtk.ResponseType.OK ]:
      return None
  finally:
    loop.hide()

  return {
    'parameters' : loop.params.representation(),
  }
