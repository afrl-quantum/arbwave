# vim: ts=2:sw=2:tw=80:nowrap

from task import Task as Base
import nidaqmx

class Digital(Base):
  task_type = 'do'
  task_class = nidaqmx.DigitalOutputTask
