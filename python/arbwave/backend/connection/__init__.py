# vim: ts=2:sw=2:tw=80:nowrap
"""
Connections to all backends.  Backends can either local or remote.
"""

# used to locate drivers within a relative import using import_module below
THISPACKAGE = 'arbwave.backend.connection'

import os, traceback, logging, importlib
from os import path
from logging import debug, DEBUG
import Pyro.core
from . import pyro
from ... import options

__all__=['Local', 'Remote']

PYRO_MAXCONNECTIONS = 1024

class Local(object):
  def __init__(self):
    super(Local,self).__init__()
    self.klasses  = dict()
    self.active   = dict()

    DRIVERS = path.join( path.dirname( __file__ ), path.pardir, 'drivers' )
    for P in os.listdir(DRIVERS):
      if path.isdir( path.join(DRIVERS,P) ):
        try:
          # do an explicit relative import of driver
          m = importlib.import_module('..drivers.'+P, THISPACKAGE)
          D = m.Driver
          if D.prefix in self.klasses:
            raise NameError("Prefix of driver already used: '"+D.prefix+"'")

          if options.simulated and not D.has_simulated_mode:
            raise NotImplementedError(
              'Cannot load driver in simulated mode: ' + D.prefix
            )

          self.klasses[D.prefix] = D
        except Exception, e:
          print "could not import backend '" + P + "'"
          if logging.root.getEffectiveLevel() <= (DEBUG-1):
            debug( e )
            debug( traceback.format_exc() )

  def __del__(self):
    self.close()

  def close(self):
    while self.active:
      prefix, driver = self.active.popitem()
      debug('closing driver: %s', prefix)
      del driver

  def __iter__(self):
    for k,D in self.klasses.items():
      if k not in self.active: self.active[k] = D()
      yield self.active[k]


  def list(self):
    """helper for pyro connection"""
    return list(self)


def serve():
  Pyro.config.PYRO_MAXCONNECTIONS = PYRO_MAXCONNECTIONS
  S = pyro.Service()
  S( backend=pyro.Wrapper(S.daemon, Local()) )


class Remote(pyro.Proxy):
  def __init__(self, host, name='backend'):
    p = Pyro.core.getProxyForURI('PYROLOC://{}:7766/{}'.format(host, name))
    super(Remote,self).__init__(p)

  def __del__(self):
    # Free the remote object dictionary.
    self._clear()

  def __iter__(self):
    return iter(self.list())

  def __getitem__(self,i):
    return self.list()[i]
