# vim: ts=2:sw=2:tw=80:nowrap

from base import Base

class Backplane(Base):
  """Base Backplane channel class"""
  def __init__(self,name, destinations=list(), invertible=False, **kwargs):
    Base.__init__(self,name,**kwargs)
    self.dest = destinations
    self.inv  = invertible

  def __repr__(self):
    return "'{n}' : ".format(n=self.name) + repr(self.dest)
