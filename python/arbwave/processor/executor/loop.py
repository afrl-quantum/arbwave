# vim: ts=2:sw=2:tw=80:nowrap

import re
import numpy as np

from ...tools.print_units import M

nan = float('nan')


class Make:
  def __init__(self, settings, datalogdb):
    self.settings = settings
    self.datalogdb = datalogdb

  def __call__(self, *args, **kwargs):
    return Executor(settings=self.settings,
                    datalogdb=self.datalogdb,
                    *args, **kwargs)()

class Executor:
  def __init__(self, runnable, Globals, settings, datalogdb):
    self.runnable = runnable
    self.Globals = Globals

    self.parameters = settings['parameters']
    V = self.get_columns( self.parameters )
    self.variables = dict()
    for i in range(len(V)):
      if V[i][0] in self.variables: continue # don't overwrite
      self.variables[ V[i][0] ] = { 'order':i, 'value':nan, 'isglobal':V[i][1] }
    # now get sorted unique list of variables
    V = sorted(self.variables.items(), key = lambda v: v[1]['order'])

    self.logger = datalogdb.get(
      columns = tuple([ vi[0] for vi in V]
                      + ['Merit'] + self.runnable.extra_data_labels()),
      title = 'Loop Parameters/Results',
    )

  def __call__(self):
    class ORun:
      def onstart(OSelf):
        self.runnable.onstart()
      def onstop(OSelf):
        self.runnable.onstop()
      def run(OSelf):
        self._for_loop_main()

    return ORun()


  def _for_loop_main(self):
    self.logger.show()
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
    self.logger.add( *M(results) )


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

def print_loop(settings, run_label):
  def print_for_loop(p, tabs):
    if not p['enable']:
      return

    if p['isglobal']:
      print(tabs, 'global', p['name'])
    print(tabs, 'for', p['name'], 'in', p['iterable'], ':')
    tabs += '\t'
    if 'children' in p:
      for child in p['children']:
        print_for_loop(child, tabs)
    else:
      print(tabs, 'execute(', run_label, ')')

  for p in settings['parameters']:
    print_for_loop(p, '\t')
