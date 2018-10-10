# vim: ts=2:sw=2:tw=80:nowrap
"""
Connections to all backends.  Backends can either local or remote.
"""

# used to locate drivers within a relative import using import_module below
THISPACKAGE = 'arbwave.backend.connection'

import sys, os, traceback, logging, importlib
from os import path
from logging import log, debug, DEBUG
import Pyro4

import physical

from ... import options
from ...tools import graphs
from ...tools.float_range import float_range

__all__=['Local', 'Remote', 'serve', 'factory']

LOCALHOST = 'localhost'
DRIVER_DIR = path.join( path.dirname( __file__ ), path.pardir, 'drivers' )
PYRO4_PORT = 1400


# basic types need conversion for config_templates (at least for now)
base_types = {'int':int, 'float':float, 'str':str, 'bool':bool}

def config_types_to_dict(t):
  return dict(__class__='arbwave.config.types', type=t.__name__)

def config_dict_to_types(clsname, D):
  assert clsname == 'arbwave.config.types', 'mismatch dict on deserializing'
  return base_types[D['type']]

Pyro4.util.SerializerBase.register_dict_to_class(
  'arbwave.config.types', config_dict_to_types)
Pyro4.util.SerializerBase.register_class_to_dict(type, config_types_to_dict)

# range must have conversion
def range_from_dict(clsname, D):
  assert clsname == 'range', 'mismatch on deserialization'
  return range(D['start'], D['stop'], D['step'])

def range_to_dict(r):
  return dict(__class__='range', start=r.start, stop=r.stop, step=r.step)

Pyro4.util.SerializerBase.register_dict_to_class(
  range.__name__, range_from_dict)
Pyro4.util.SerializerBase.register_class_to_dict(range, range_to_dict)

# float_range must have conversion
Pyro4.util.SerializerBase.register_dict_to_class(
  float_range.__name__, float_range.from_dict)
Pyro4.util.SerializerBase.register_class_to_dict(
  float_range, float_range.to_dict)

def register_graph_serializers():
  # Graphs must have conversion
  Pyro4.util.SerializerBase.register_dict_to_class(
    graphs.DiGraph.__name__, graphs.DiGraph.from_dict)
  Pyro4.util.SerializerBase.register_class_to_dict(
    graphs.DiGraph, graphs.DiGraph.to_dict)

### We have to make sure that physical quantities are serializable:
Pyro4.util.SerializerBase.register_dict_to_class(
  physical.Quantity.SERIALIZATION_NAME, physical.Quantity.from_dict)
Pyro4.util.SerializerBase.register_class_to_dict(
  physical.Quantity, physical.Quantity.to_dict)



def get_driver_list():
  return [
    P for P in os.listdir(DRIVER_DIR)
    if P[:2] != '__' and path.isdir( path.join(DRIVER_DIR,P) )
  ]

class Local(object):
  """
  Connection to local instances of drivers and hardware.
  """
  def __init__(self, prefix, remote_backend=False):
    super(Local,self).__init__()
    self.klasses  = dict()
    self._drivers  = dict()
    self._prefix   = prefix

    for P in get_driver_list():
      if P in options.disabled_drivers:
        continue

      try:
        # do an explicit relative import of driver
        m = importlib.import_module('..drivers.'+P, THISPACKAGE)
        D = m.Driver
        if remote_backend and not D.allow_remote_connection:
          # some drivers can only be serviced by a pure Local instance
          continue

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

  @Pyro4.expose
  @property
  def drivers(self):
    return self._drivers

  @Pyro4.expose
  @property
  def prefix(self):
    return self._prefix

  @Pyro4.expose
  @prefix.setter
  def prefix(self, value):
    self._prefix = value

  @Pyro4.expose
  def close(self):
    import logging # sometimes needed on close
    while self._drivers:
      prefix, driver = self._drivers.popitem()
      logging.debug('closing driver: %s', prefix)
      try:
        driver.close() # explicitly close to avoid garbage collector problems
        del driver
      except:
        try: traceback.print_exc()
        except: pass
        print('driver not cleanly closed: ', prefix)

  @Pyro4.expose
  def open(self):
    for k,D in self.klasses.items():
      # we don't prefix drivers that are local only.
      pfx = self._prefix if D.allow_remote_connection else ''

      k = D.format_prefix(pfx)
      if k not in self._drivers:
        self._drivers[k] = D(pfx)

  def __getitem__(self,i):
    return self._drivers[i]

  @Pyro4.expose
  def get_compatibility(self):
    """
    Get compatibilty options between frontend and backend
    """
    return dict(
      graphs = graphs.get_valid(),
    )

  @Pyro4.expose
  def set_compatibility(self, **kw):
    """
    Get compatibilty options between frontend and backend
    """
    if 'graphs' in kw:
      g = graphs.negotiate(kw['graphs'])
      register_graph_serializers()
      debug('Negotiated common directed graph format: %s', g)


class Root(Local):
  """
  The front door for all remote requests into local connections to
  drivers/devices.
  """
  ROOT_NAME = 'backend'

  def __init__(self, daemon, *a, **kw):
    super(Root, self).__init__(*a, **kw)
    self.daemon = daemon
    self.uri = daemon.register(self, self.ROOT_NAME)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()

  @Pyro4.expose
  def close(self):
    """close all wrappers and free memory, except for self"""
    debug('remove all objects (except self) from daemon')

    daemon_obj = self.daemon.objectsById['Pyro.Daemon']
    OBJs = set(self.daemon.objectsById.values()) - {self, daemon_obj}
    for obj in OBJs:
      log(DEBUG-1, 'disconnecting %s', obj)
      self.daemon.unregister(obj)

    log(DEBUG-1, 'daemon connections still remaining: %s',
        self.daemon.objectsById)
    debug('close all drivers')
    super(Root,self).close()

  @Pyro4.expose
  def open(self):
    """
    First opens up all drivers, then recursively registers all components of the
    drivers that has to be exposed to the front end.
    """
    super(Root, self).open()
    for prefix, driver in self.drivers.items():
      debug('registering driver with Pyro4: %s', prefix)
      self.daemon.register(driver)

      debug('registering all Pyro4 components of driver: %s', prefix)
      for obj in driver.get_all_frontend_objects():
        log(DEBUG-1, 'Pyro4 registering: %s', obj)
        self.daemon.register(obj)


def serve(ns = None):
  """
  Serve the backend over Pyro4 in a headless manner.
  Options:
    ns : the host:port pair of the nameserver, in case it is not possible to
         find it by broadcast.
         NOT using this yet.  Have to find a way to make this clean.  Just using
         static port for now.
  """
  daemon = Pyro4.Daemon(port = PYRO4_PORT)
  with Root(daemon, prefix=None, remote_backend=True) as root:
    debug('PYRO4 URI : %s', root.uri)
    daemon.requestLoop()


class Remote(Pyro4.Proxy):
  def __init__(self, host, prefix='', name=Root.ROOT_NAME):
    sys.excepthook = Pyro4.util.excepthook

    super(Remote,self).__init__('PYRO:{}@{}:{}'.format(name, host, PYRO4_PORT))

    if self.prefix != prefix:
      if self.drivers:
        # re-open all drivers with the new prefix
        self.close()
        self.open()
      self.prefix = prefix

    # negotiate exchange formats
    self.negotiate()

  def __del__(self):
    self.close()

  def __getitem__(self,i):
    return self.drivers[i]

  def negotiate(self):
    """
    Negotiate compatibilty components between frontend and backend
    """
    D = self.get_compatibility()
    if 'graphs' not in D:
      raise RuntimeError('Remote side will not negotiate directed graphs!')

    debug('negotiating directed graph formats')
    g = graphs.negotiate(D['graphs'])
    self.set_compatibility(graphs = [g])
    register_graph_serializers()
    debug('Negotiated common directed graph format: %s', g)


def factory(prefix, host):
  if host == LOCALHOST:
    return Local(prefix)
  else:
    return Remote(host, prefix)
