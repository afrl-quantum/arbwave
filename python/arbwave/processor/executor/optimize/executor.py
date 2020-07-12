# vim: ts=2:sw=2:tw=80:nowrap

import re
from logging import warning, debug, info, error

import numpy as np
from matplotlib import mlab

import physical

from ....tools.print_units import M
from .algorithms import algorithms

# some really big number to use for bad constraint merits.  sys.float_info.max
# used to be used, but it tends to cause floating point errors--probably because
# the algorithms do some additional math with the merit values.
MAX_MERIT = 1e200


class Make:
  def __init__(self, settings, datalogdb):
    self.settings = settings
    self.datalogdb = datalogdb

  def __call__(self, *args, **kwargs):
    return Executor(settings=self.settings,
                    datalogdb=self.datalogdb,
                    *args, **kwargs)()

class Executor:
  def __init__(self, runnable, Globals, settings, datalogdb,
               cache_tolerance=1e-3):
    self.runnable = runnable
    self.Globals = Globals

    self._cache = None
    self.results = dict()
    self.cache_tolerance = cache_tolerance
    self.skipped_evals = 0

    self.pnames = list()
    self.params = list()
    for P in settings['parameters']:
      if P['enable']:
        self.pnames.append( P['name'] )
        self.params.append( (
          M(eval(P['name'],  Globals)),
          M(eval(P['min'],   Globals)),
          M(eval(P['max'],   Globals)),
          M(eval(P['scale'], Globals)),
        ) )

    self.params = np.array( self.params )

    self.constraints = settings['constraints']

    self.logger = datalogdb.get(
      columns = tuple(self.pnames+['Merit']+self.runnable.extra_data_labels()),
      title = 'Optimization Results',
    )

    self.algorithms = prep_algorithms(settings)
    self.repetitions = settings['repetitions']


  def __call__(self):
    class ORun:
      def onstart(OSelf):
        self.runnable.onstart()

      def onstop(OSelf):
        self.runnable.onstop()

      def run(OSelf):
        self.logger.show()
        x0 = self.params[:,0]
        scale = self.params[:,3]
        # first unscale all parameters
        x0 /= scale
        for name, kwargs in self.algorithms:
          self.evals = 0
          x0, merit = algorithms[name]['func'](self._call_func, x0, **kwargs)
          info('{} optimization: final state:%s, merit:%g', x0*scale, merit)
          info('{} optimization: Number waveforms executed: %d', self.evals)

        self.save_globals( x0 * scale )

        return True

    return ORun()


  def save_globals(self, x):
    # only try to make global variables that are fundamental types
    # (str,int,float, ...)
    globalize = [ i for i in self.pnames if not re.search('["\'\[]', i) ]
    if globalize:
      exec('global ' + ','.join( globalize ))
    for i in range(len(x)):
      exec('{n} = {v}'.format(n=self.pnames[i], v=M(x[i])), self.Globals)


  def _call_func(self, x):
    # before using x, ensure that it is rescaled
    x = x * self.params[:,3] # dont multiply in-place

    cached = self.lookup(x)
    if cached is not None:
      self.logger.add( *M(list(x) + list(cached)) )
      self.skipped_evals += 1
      # the zeroth element of cached is the merit
      return cached[0]

    self.save_globals(x)

    # now, test constraints before running the function
    # first test parameter range constraints
    if np.any(x < self.params[:,1]) or np.any(x > self.params[:,2]):
      warning('Optimization parameter range constraint(s) failed')
      c_failed = True
    else:
      # now test all user-provided constraint equations
      c_failed = [ condition
        for condition, enabled in self.constraints.items()
          if enabled and not eval(condition, self.Globals)
      ]
      if c_failed:
        warning('Optimization constraint equantion(s) failed: {}'
                .format(c_failed))

    if c_failed:
      result = [MAX_MERIT] + [0]*len(self.runnable.extra_data_labels())
    else:
      def A(r):
        # need better test like "if iterable"
        if type(r) in [ np.ndarray, list, tuple ]:
          return np.array(r)
        else:
          return np.array([r])

      self.evals += 1

      # average result for the given number of repetitions
      result = np.array([
        A(self.runnable.run()) for i in range(self.repetitions)
      ]).mean(axis=0)

      # result is necessarily a numpy array by now
      self.logger.add( *M(list(x) + list(result)) )
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



def prep_algorithms(settings):
  sorted_algorithms = sorted(settings['algorithms'].items(),
                             key = lambda alg_opts : alg_opts[1]['order'])
  return [
    (alg,
      {
        arg : argopt['value']
        for arg, argopt in algopt['parameters'].items()  if argopt['enable']
      }
    )
    for alg, algopt in sorted_algorithms  if algopt['enable']
  ]


def print_optimizers(settings, run_label, Globals):
  print('\t# Optimizing with following constraints:')
  pnames = list()
  x0 = list()
  for p in settings['parameters']:
    if not p['enable']:
      continue
    print('\t#', p['min'], '<=', p['name'], '<=', p['max'])
    pnames.append(p['name'])
    x0.append(eval(p['name'], Globals))
  for c, c_enable in settings['constraints'].items():
    if c_enable:
      print('\t#', c)
  print('\tx0 = [', ', '.join(pnames), ']')

  func = '{}<{}>'.format(run_label, settings['repetitions'])
  for alg, kwargs in prep_algorithms(settings):
    print('\t{}({}, x0={}, **{})'.format(alg, func, x0, kwargs))
