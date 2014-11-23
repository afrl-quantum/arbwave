# vim: ts=2:sw=2:tw=80:nowrap

from subdevice import Subdevice as Base
import nidaqmx

class Digital(Base):
  subdev_type = 'do'
