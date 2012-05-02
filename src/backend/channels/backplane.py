# vim: ts=2:sw=2:tw=80:nowrap

from base import Base

class Backplane(Base):
  """Base Backplane channel class"""
  def __init__(self,name, destinations=list(), invertible=False):
    Base.__init__(self,name)
    self.dest = destinations
    self.inv  = invertible

