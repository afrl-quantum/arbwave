# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, DEBUG
from base import Base

class Backplane(Base):
  """Base Backplane channel class"""
  _type = 'backplane'
  def __init__(self,src, destinations=list(), invertible=False, **kwargs):
    Base.__init__(self,src,**kwargs)
    self.src  = src
    self.dest = destinations
    self.inv  = invertible
    log(DEBUG-1, 'creating backplane channel: (%s --> %s)', self.src, self.dest)

  def __repr__(self):
    return "'{n}' : ".format(n=self.src) + repr(self.dest)
