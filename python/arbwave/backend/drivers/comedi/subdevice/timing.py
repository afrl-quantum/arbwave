# vim: ts=2:sw=2:tw=80:nowrap

from subdevice import Subdevice as Base
import nidaqmx
import ctypes_comedi as c
import numpy as np

class Timing(Base):
  subdev_type = 'to'
  
  #timing subdevices include the GPCTs and the FREQ OUT channel
  #this class should in the future include a cmd_config overwrite to
  #configure these channels for their unique output commands
  #and also read off settings from the 'clocks' window in arbwave 
  
  
  def __init__(self, route_loader, device, subdevice, name_uses_subdev=False):
    
    self.device = device
    self.subdevice = subdevice
    debug( 'loading comedi subdevice %s', self )
    self.task = True #TO DO: get rid of this
    self.channels = dict()
    self.clocks = None
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0
    self.chan_index_list = list()
    self.cmd = c.comedi_cmd()
    
    self.index = str(self.subdevice - c.comedi_find_subdevice_by_type(self.fd,c.COMEDI_SUBD_COUNTER,0))
    
    if name_uses_subdev: devname = '{}{}'.format(self.subdev_type, subdevice)
    else:                devname = 'Ctr'+self.index
    name = '{}/{}'.format(device, devname)
    Base.__init__(self, name=name)
    self.base_name = devname
    
    print name, "timing chan"
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
