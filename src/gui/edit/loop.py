# vim: ts=2:sw=2:tw=80:nowrap

import gtk

import sys, re, pydoc

import numpy as np
from matplotlib import mlab

import helpers
from helpers import GTVC

from optimize.show import Show
from spreadsheet import keys

class Parameters(gtk.ListStore):
  NAME    = 0
  MIN     = 1
  MAX     = 2
  STEP    = 3
  ISGLOBAL= 4
  ENABLE  = 5

  DEFAULT = ('', '0', '10', '1', False, True)

  def __init__(self):
    gtk.ListStore.__init__(self,
      str, #name
      str, #min
      str, #max
      str, #step
      bool,#global
      bool,#enable
    )



def drag_motion(w, ctx, x, y, time):
  mask = w.window.get_pointer()[2]
  if mask & gtk.gdk.CONTROL_MASK:
    ctx.drag_status( gtk.gdk.ACTION_COPY, time )


class LoopView(gtk.Dialog):
  def __init__(self, settings, Globals, title='Loop Parameters',
               parent=None, target=None, model=False):
    actions = [
      gtk.STOCK_OK,     gtk.RESPONSE_OK,
      gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
    ]
    flags = gtk.DIALOG_DESTROY_WITH_PARENT
    if model:
      flags |= gtk.DIALOG_MODAL
      actions.pop(2)
      actions.pop(2)

    gtk.Dialog.__init__( self, title, parent, flags, tuple(actions) )

    self.set_default_size(550, 600)
    self.set_border_width(10)


    self.params = Parameters()
    if 'parameters' in settings:
      for p in settings['parameters']:
        self.params.append(
          (p['name'], p['min'], p['max'], p['step'], p['isglobal'], p['enable'])
        )
    else:
      self.params.append( Parameters.DEFAULT )

    V = self.view = gtk.TreeView( self.params )
    V.set_reorderable(True)
    #V.connect('drag-begin', begin_drag, self.window)
    #V.connect('drag-end', end_drag, self.window, waveforms)
    V.connect('drag-motion', drag_motion)
    V.connect('key-press-event', self.view_keypress_cb)
    R = {
      'name'    : gtk.CellRendererText(),
      'min'     : gtk.CellRendererText(),
      'max'     : gtk.CellRendererText(),
      'step'    : gtk.CellRendererText(),
      'isglobal': gtk.CellRendererToggle(),
      'enable'  : gtk.CellRendererToggle(),
    }
    R['name'].set_property( 'editable', True )
    R['name'].connect('edited', helpers.set_item, self.params, Parameters.NAME)
    R['min'].set_property( 'editable', True )
    R['min'].connect( 'edited', helpers.set_item, self.params, Parameters.MIN )
    R['max'].set_property( 'editable', True )
    R['max'].connect( 'edited', helpers.set_item, self.params, Parameters.MAX )
    R['step'].set_property( 'editable', True )
    R['step'].connect('edited', helpers.set_item, self.params, Parameters.STEP)
    R['isglobal'].set_property( 'activatable', True )
    R['isglobal'].connect('toggled', helpers.toggle_item, self.params, Parameters.ISGLOBAL)
    R['enable'].set_property( 'activatable', True )
    R['enable'].connect('toggled', helpers.toggle_item, self.params, Parameters.ENABLE)

    C = {
      'name' : GTVC('Variable', R['name'], text=Parameters.NAME),
      'min' : GTVC('Min', R['min'], text=Parameters.MIN),
      'max' : GTVC('Max', R['max'], text=Parameters.MAX),
      'step' : GTVC('Step Size', R['step'], text=Parameters.STEP),
      'isglobal' : GTVC('Global', R['isglobal']),
      'enable' : GTVC('Enable', R['enable']),
    }
    C['isglobal'].add_attribute(R['isglobal'], 'active', Parameters.ISGLOBAL)
    C['enable'].add_attribute(R['enable'], 'active', Parameters.ENABLE)
    V.append_column( C['name'] )
    V.append_column( C['min'] )
    V.append_column( C['max'] )
    V.append_column( C['step'] )
    V.append_column( C['isglobal'] )
    V.append_column( C['enable'] )

    V.show()

    scroll = gtk.ScrolledWindow()
    scroll.set_size_request(-1,-1)
    scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    scroll.add( V )
    scroll.show()
    self.vbox.pack_start( scroll )


  def view_keypress_cb(self, entry, event):
    if event.keyval == keys.INSERT:
      model, rows = self.view.get_selection().get_selected_rows()
      # we convert paths to row references so that references are persistent
      if rows:
        rows = [ model.get_iter(p)  for p in rows ]
        for row in rows:
          model.insert_before( row, Parameters.DEFAULT )
      else:
        model.append( Parameters.DEFAULT )
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
  def __init__(self, run_label, settings):
    self.run_label = run_label
    self.settings = settings

  def __call__(self, *args, **kwargs):
    S = self.settings.get(self.run_label,dict())
    e = Executor( settings=S, *args, **kwargs )
    S = e.get_settings()
    if S:
      self.settings[self.run_label] = S
    return e()

class Executor:
  def __init__(self, runnable, Globals, settings):
    self.runnable = runnable
    self.Globals = Globals

    self.show = None

    loop = LoopView(settings, Globals)
    self.cancelled = False
    try:
      if loop.run() not in [ gtk.RESPONSE_OK ]:
        print 'cancelled!'
        self.cancelled = True
        return
    finally:
      loop.hide()

    self.parameters = list()
    for p in loop.params:
      self.parameters.append(
        { 'name'      : p[loop.params.NAME],
          'min'       : p[loop.params.MIN],
          'max'       : p[loop.params.MAX],
          'step'      : p[loop.params.STEP],
          'isglobal'  : p[loop.params.ISGLOBAL],
          'enable'    : p[loop.params.ENABLE],
        }
      )

    self.show = Show(
      columns=[ i['name']  for i in self.parameters if i['enable'] ]
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
        self._loop_func()

    if self.cancelled: return Cancelled()
    else:              return ORun()


  def _loop_func(self):
    self.show.show()
    x = list()
    for p in self.parameters:
      if not p['enable']:
        continue
      x.append( eval( p['min'], self.Globals ) )

    self._loop_i( x, 0, 0 )


  def _loop_i(self, x, i, pi):
    p = self.parameters[pi]
    if p['enable']:
      if p['isglobal'] and not re.search('["\'\[]', p['name']):
        exec 'global ' + p['name']

      x[i] = eval( p['min'], self.Globals )
      while x[i] < eval(p['max'], self.Globals):
        if p['isglobal']:
          exec '{n} = {xi}'.format(n=p['name'], xi=x[i]) in self.Globals
        self._loop_nexti(x,i+1,pi)
        x[i] += eval(p['step'], self.Globals)
    else:
      self._loop_nexti(x,i,pi)

  def _loop_nexti(self, x, i, pi):
    if pi < (len(self.parameters)-1):
      self._loop_i(x, i, pi+1)
    else:
      self.runnable.run()
      self.show.add( *x )



main_settings = dict()

def main():
  import traceback, pprint
  from optimize import test
  e = Make('func', main_settings)( test.func(), globals() )

  print 'e: ', e
  return e
