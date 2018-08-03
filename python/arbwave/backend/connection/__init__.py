# vim: ts=2:sw=2:tw=80:nowrap
"""
Connections to all backends.  Backends can either local or remote.
"""

# used to locate drivers within a relative import using import_module below
THISPACKAGE = 'arbwave.backend.connection'

import os, traceback, logging, importlib
from os import path
from logging import log, debug, DEBUG
import Pyro.core
from ... import options
from ...tools import graphs
from . import pyro

__all__=['Local', 'Remote']

PYRO_MAXCONNECTIONS = 1024
LOCALHOST = 'localhost'
DRIVER_DIR = path.join( path.dirname( __file__ ), path.pardir, 'drivers' )

def get_driver_list():
  return [
    P for P in os.listdir(DRIVER_DIR)
    if P[:2] != '__' and path.isdir( path.join(DRIVER_DIR,P) )
  ]

class Local(object):
  def __init__(self, prefix, remote_backend=False):
    super(Local,self).__init__()
    self.klasses  = dict()
    self.drivers  = dict()
    self.prefix   = prefix

    for P in get_driver_list():
      if remote_backend and P == 'external' or P in options.disabled_drivers:
        # we only let the external driver be service by a pure Local instance
        continue

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
      except Exception as e:
        print("could not import backend '{}'".format(P))
        if logging.root.getEffectiveLevel() <= (DEBUG-1):
          debug( e )
          debug( traceback.format_exc() )

  def __del__(self):
    self.close()

  def close(self):
    while self.drivers:
      prefix, driver = self.drivers.popitem()
      try: debug('closing driver: %s', prefix)
      except: pass # sometimes fails on exit
      try:
        driver.close() # explicitly close to avoid garbage collector problems
        del driver
      except:
        try: traceback.print_exc()
        except: pass
        print('driver not cleanly closed: ', prefix)

  def open(self):
    for k,D in self.klasses.items():
      pfx = self.prefix if k != 'External' else ''

      k = D.format_prefix(pfx)
      if k not in self.drivers:
        self.drivers[k] = D(pfx)

  def __getitem__(self,i):
    return self.drivers[i]

  def get_compatibility(self):
    """
    Get compatibilty options between frontend and backend
    """
    return dict(
      graphs = graphs.get_valid(),
    )

  def set_compatibility(self, **kw):
    """
    Get compatibilty options between frontend and backend
    """
    if 'graphs' in kw:
      g = graphs.negotiate(kw['graphs'])
      debug('Negotiated common directed graph format: %s', g)



def serve():
  class RootWrapper(pyro.Wrapper):
    def close(self):
      """close all wrappers and free memory, except for self"""
      debug('remove all Wrapper objects (except self) from daemon')
      for obj, name in self.daemon.implementations.values():
        if obj == self or type(obj) == Pyro.core.DaemonServant:
          continue
        log(DEBUG-1, 'disconnecting %s', obj)
        self.daemon.disconnect( obj )
      log(DEBUG-1, 'daemon connections still remaining: %s',
          self.daemon.implementations)
      debug('close all drivers')
      self.obj.close()

  Pyro.config.PYRO_MAXCONNECTIONS = PYRO_MAXCONNECTIONS
  S = pyro.Service()
  S( backend=RootWrapper(S.daemon, Local(prefix=None, remote_backend=True)) )


class Remote(pyro.Proxy):
  def __init__(self, host, prefix='', name='backend'):
    p = Pyro.core.getProxyForURI('PYROLOC://{}:7766/{}'.format(host, name))
    super(Remote,self).__init__(p)
    if self.prefix != prefix:
      if self.drivers:
        # re-open all drivers with the new prefix
        self.close()
        self.open()
      self.prefix = prefix

  def __del__(self):
    self.close()

  def close(self):
    debug('freeing remote object dictionary')
    self._clear()
    debug('closing remote drivers')
    self.obj.close()

  def __getitem__(self,i):
    return self.drivers[i]

  def negotiate(self):
    """
    Negotiate compatibilty components between frontend and backend
    """
    D = self.get_compatibility()
    if 'graphs' not in D:
      raise RuntimeError('Remote side will not negotiate directed graphs!')
    self.set_compatibility(
      graphs = [graphs.negotiate(D['graphs'])],
    )


def factory(prefix, host):
  if host == LOCALHOST:
    return Local(prefix)
  else:
    return Remote(host, prefix)
