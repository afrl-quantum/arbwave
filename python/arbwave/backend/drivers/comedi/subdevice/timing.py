# vim: ts=2:sw=2:tw=80:nowrap

from subdevice import Subdevice as Base
import nidaqmx
import ctypes_comedi as c
import numpy as np

class Timing(Base):
  subdev_type = 'to'

  def set_clocks(self, clocks):
    if self.clocks != clocks:
      self.clocks = clocks
      self.set_config( force=True )


  def add_channels(self):
    print "add chans to"

  def get_config_template(self):
    template = Base.get_config_template(self)
    template.pop('use-only-onboard-memory')
    return template
