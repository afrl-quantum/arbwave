# vim: ts=2:sw=2:tw=80:nowrap

from base import Base

class Analog(Base):
  """Base Analog channel class"""
  def __init__(self,name):
    Base.__init__(self,name)

