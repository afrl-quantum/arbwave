# vim: ts=2:sw=2:tw=80:nowrap

from base import Base

class Backplane(Base):
  """Base Backplane channel class"""
  def __init__(self,src, destinations=list(), invertible=False, **kwargs):
    Base.__init__(self,src,**kwargs)
    self.src  = src
    self.dest = destinations
    self.inv  = invertible

  def __repr__(self):
    return "'{n}' : ".format(n=self.src) + repr(self.dest)
