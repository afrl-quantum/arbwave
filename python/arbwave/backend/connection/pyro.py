# vim: ts=2:sw=2:tw=80:nowrap

import Pyro.core
from logging import critical, debug, DEBUG
import traceback

class PyroResponse(object):
  """
  Simple class to help communicate URI/name of pyro served object.
  """
  def __init__(self, name):
    self.name = name
  def __str__(self):
    return self.name
  def __repr__(self):
    return self.name

class Wrapper(Pyro.core.ObjBase):
  """
  Wrapper for classes that will be serviced by a Pyro daemon.
  """
  def __init__(self, daemon=None, obj=None, klass=None):
    """
    Wrap an object to be served over pyro connection.
      options:
        daemon:  pyro daemon used to recursively wrap objects.  If this is not
                 set, recursion will not occur. [Default None]
           obj:  object to wrap. if this is not set, klass should be set
                 [Default None]
    """
    super(Wrapper,self).__init__()
    self.daemon = daemon
    self.obj = obj
    self.klass = klass
    assert self.obj or self.klass, 'Specify at least one of obj or klass'

  def __del__(self):
    """
    Clean up the wrapper and its objects.
    """
    # note that del is not effective if the ref count != 1
    del self.obj

  def _attributes(self):
    return [
      i for i in dir(self.obj)
      if not ( i.startswith('_') or callable(getattr(self.obj,i)) )
    ]

  def _callables(self):
    return [
      i for i in dir(self.obj)
      if (not i.startswith('_')) and callable(getattr(self.obj,i))
    ]

  def __call__(self):
    """
    instantiate the klass if not already instantiated
    """
    if not self.obj:
      self.obj = self.klass()
    return self

  def _getAttr(self, attr):
    return self._wrap_all_results( getattr(self.obj, attr) )

  def _setAttr(self, attr, value):
    return setattr(self.obj, attr, value)

  def _execFunc(self, func, *a, **kw):
    return self._wrap_all_results( getattr(self.obj, func)(*a, **kw) )

  def _wrap_all_results(self, retval):
    """
    Pyro service recursion for collections.  We will only support basic python
    data types (list, tuple, set, dict) and only one level deep.
    """
    if not self.daemon:
      return retval # no recursion

    # we are going to recurse the pyro services.  This protection is going to be
    # relatively simple and will only look one level into lists, tuples, sets,
    # and dictionaries.
    if type(retval) in [list, tuple, set]:
      return type(retval)([self._wrap(i) for i in retval])
    elif type(retval) in [dict]:
      return {k:self._wrap(v) for k,v in retval.items()}
    else:
      return self._wrap( retval )

  def _wrap(self, obj):
    """
    Tests an object to see whether an automatic pyro served recursion should
    occur.
    """
    if hasattr(obj, '_pyro_') and obj._pyro_:
      name = '{}.{}/{}'.format(obj.__module__, obj.__class__.__name__, str(obj))
      D = {name:klass for klass,name in self.daemon.implementations.values()}
      if name not in D:
        # create wrapper and register
        wrapper = Wrapper( self.daemon, obj )
        self.daemon.connect(wrapper, name)
      elif D[name].obj != obj:
        # this obviously assumes that the object is a Wrapper
        raise RuntimeError('two objects with same descriptor?: '+name)
      return PyroResponse( name )
    else:
      # we just return the raw object--no pyro wrapping
      return obj




class Exec(object):
  """
  Representation of remote functions.
  """
  def __init__(self, proxy, fun):
    super(Exec,self).__init__()
    self.proxy = proxy
    self.fun = fun
  def __call__(self, *a, **kw):
    try:
      return self.proxy._proxy_all_results(
        self.proxy.obj._execFunc( self.fun, *a, **kw )
      )
    except:
      critical( 'Could not remotely call \'%s(%s,%s)\'', self.fun, a, kw )
      traceback.print_exc()
      raise


class Proxy(object):
  """
  Proxy for remote classes that are serviced from a remote Pyro daemon.
  """
  _db = dict()
  _local_attrib = list()

  @staticmethod
  def _clear():
    for i in Proxy._db.keys():
      del Proxy._db[i]

  def __init__(self, obj):
    super(Proxy,self).__init__()
    self.obj = obj
    self._attribs = self.obj._attributes()

  @property
  def _callables(self):
    return self.obj._callables()

  def __str__(self):
    return Exec(self, '__str__')()
  def __repr__(self):
    return Exec(self, '__repr__')()

  def __getattr__(self, attr):
    if attr in self._attribs:
      return self._proxy_all_results( self.obj._getAttr(attr) )
    else:
      return Exec(self, attr)

  def __setattr__(self, attr, value):
    if attr in ['obj', '_attribs'] + self._local_attrib:
      return object.__setattr__( self, attr, value )
    elif attr in self._attribs:
      return self.obj._setAttr(attr, value)
    else:
      raise RuntimeError('can only set existing attributes on remote object')

  def _proxy_all_results(self, retval):
    """
    Pyro service recursion for collections.  We will only support basic python
    data types (list, tuple, set, dict) and only one level deep.
    """
    # we are going to recurse the pyro services.  This protection is going to be
    # relatively simple and will only look one level into lists, tuples, sets,
    # and dictionaries.
    if type(retval) in [list, tuple, set]:
      return type(retval)([self._proxy(i) for i in retval])
    elif type(retval) in [dict]:
      return {k:self._proxy(v) for k,v in retval.items()}
    else:
      return self._proxy( retval )

  def _proxy(self, obj):
    """
    Tests each first-level object received for pyro recursion.  If the object is
    of type PyroResponse, we automatically establish a Proxied connection to
    that object.
    """
    if type(obj) == PyroResponse:
      if obj.name in self._db:
        return self._db[obj.name]
      else:
        uri = self.obj.URI.clone()
        uri.protocol = 'PYROLOC'
        uri.objectID = obj.name
        p = Proxy( Pyro.core.getProxyForURI(uri) )
        self._db[obj.name] = p
        return p
    else:
      return obj


class Service(object):
  def __init__(self):
    Pyro.core.initServer()
    self.daemon = Pyro.core.Daemon()

  def __call__(self, **klasses):
    for k, obj in klasses.items():
      uri = self.daemon.connect(obj, k)
      debug('connected %s to %s', obj, uri)
    self.daemon.requestLoop()
