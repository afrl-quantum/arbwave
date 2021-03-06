# vim: ts=2:sw=2:tw=80:nowrap

import numpy as np

from .subdevice import Subdevice as Base

class Timing(Base):
  subdev_type = 'to'

  #timing subdevices include the GPCTs and the FREQ OUT channel
  #this class should in the future include a cmd_config overwrite to
  #configure these channels for their unique output commands
  #and also read off settings from the 'clocks' window in arbwave
