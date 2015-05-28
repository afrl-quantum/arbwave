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

__all__=['Connection', 'Local', 'Service', 'Remote']


class Connection(object):
  def __init__(self):
    super(Connection,self).__init__()
    self.klasses  = dict()
    self.active   = dict()
    self.connect()

  def connect(self):
    raise NotImplementedError('unknown connection must be implemented')

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


class Local(Connection):
  def connect(self):
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


class Service(Local, Pyro.core.ObjBase):
  def connect(self):
    super(Service,self).connect()
    self.daemon = daemon = Pyro.core.Daemon()
    for prefix, klass in self.klasses.items():
      self.klasses[prefix] = pyro.Wrapper(self.daemon, klass=klass)

  def serve(self):
    Pyro.core.initServer()
    # for some reason, we need to set this local var...
    daemon = self.daemon
    uri = self.daemon.connect(self,'backend')

    print "The daemon runs on port:",self.daemon.port
    print "The object's uri is:",uri

    self.daemon.requestLoop()

  def list(self):
    retval = list()
    for D in self:
      if D.obj.prefix not in self.daemon.getRegistered().values():
        self.daemon.connect(D, D.obj.prefix)
      retval.append( D.obj.prefix )
    return retval


class Remote(Connection):
  def __init__(self, host):
    self.host = host
    super(Remote,self).__init__()

  def close(self):
    super(Remote,self).close()
    del self.connection

  def connect(self):
    self.connection = self.get_pyro_obj('backend')
    def mk_get_pyro(self, k):
      return lambda: pyro.Proxy( self.get_pyro_obj(k) )
    for k in self.connection.list():
      self.klasses[k] = mk_get_pyro(self,k)

  def get_pyro_obj(self, name):
    return \
      Pyro.core.getProxyForURI('PYROLOC://{}:7766/{}'.format(self.host, name))
