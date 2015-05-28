# vim: ts=2:sw=2:tw=80:nowrap

import Pyro.core

class Wrapper(Pyro.core.ObjBase):
  """
  Wrapper for classes that will be serviced by a Pyro daemon.
  """
  def __init__(self, obj=None, klass=None):
    super(Wrapper,self).__init__()
    self.obj = obj
    self.klass = klass

  def __call__(self):
    """
    instantiate the klass if not already instantiated
    """
    if not self.obj:
      self.obj = self.klass()
    return self

  def _getAttr(self,attr):
    return getattr(self.obj, attr)

  def _execFunc(self, func, *a, **kw):
    return getattr(self.obj, func)(*a, **kw)



class Exec(object):
  """
  Representation of remote functions.
  """
  def __init__(self, obj, fun):
    super(Exec,self).__init__()
    self.obj = obj
    self.fun = fun
  def __call__(self, *a, **kw):
    return self.obj._execFunc( self.fun, *a, **kw )

class Proxy(object):
  """
  Proxy for remote classes that are serviced from a remote Pyro daemon.
  """
  attribs = ['prefix', 'description', 'has_simulated_mode', 'simulated']
  def __init__(self, obj):
    super(Proxy,self).__init__()
    self.obj = obj

  def __str__(self):
    return Exec(self.obj, '__str__')()
  def __repr__(self):
    return Exec(self.obj, '__repr__')()

  def __getattr__(self, attr):
    if attr in self.attribs:
      return self.obj._getAttr(attr)
    else:
      return Exec(self.obj, attr)


def test_pyro(**klasses):
  Pyro.core.initServer()
  daemon = Pyro.core.Daemon()
  for k, obj in klasses.items():
    daemon.connect(obj, k)
  daemon.requestLoop()
