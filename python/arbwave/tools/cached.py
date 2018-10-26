# vim: ts=2:sw=2:tw=80:nowrap
import time
import threading

inf = float('inf')

__all__ = ['property']

class _dummy_lock(object):
  def __enter__(self, *a, **kw):
    pass
  def __exit__(self, *a, **kw):
    pass

class property(object):
  """
  A multi-purpose property that can:
    - use a cache and only re-evaluate after a specified time-to-live
    - replace the property class with an ordinary attribute
      (this can be reset by deleting the attribute from the instance)
    - cause all access into the non-ordinary property be controlled by a thread
      lock

  Options:
    ttl   : time-to-live for cached value [Default: float('inf')]
            if this is float('inf'), the property will be replaced by an
            ordinary value.
            If an item has been replaced (ttl=inf):
              cause it to be reset/recalculated the next time it is accessed by
              deleting the attribute from the instance
            If an item has been cached:
              By deleting the cache of this item, the next next access will
              necessarily recalculate the result:
                del obj._cache['item']
    lock  : boolean value to indicate that any access to this property in its
            functional form will be controlled via a thread lock.
  """
  def __init__(self, *a, ttl=inf, lock=False):
    self.ttl = ttl
    self.lock = _dummy_lock()
    if lock:
      self.lock = threading.RLock()

    if a:
      self(*a)

  def __repr__(self):
    return '<{}(ttl={}, lock={}) at {}>'.format(
      property.__name__,
      self.ttl,
      True if not isinstance(self.lock, _dummy_lock) else False,
      hex(id(self)),
    )

  def __call__(self, func):
    self.func = func
    self.__doc__    = getattr(func, '__doc__')
    self.__name__   = getattr(func, '__name__')
    self.__module__ = getattr(func, '__module__')
    return self

  def __get__(self, obj, klass):
    # when this is requested on a klass not an instance
    if obj is None:
      return self

    with self.lock:
      if self.ttl == inf:
        # We replace ourselves with an ordinary attribute
        value = self.func(obj)
        obj.__dict__[self.__name__] = value
        return value

      if not hasattr(obj, '_cache'):
        obj._cache = dict()

      now = time.time()
      value, last_update = obj._cache.get(self.__name__, (None,-1))

      if self.ttl > 0 and now - last_update <= self.ttl:
        # not outlived yet
        return value

      # re-evaluate and cache
      value = self.func(obj)
      obj._cache[self.__name__] = (value, now)
      return value
