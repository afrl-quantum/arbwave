# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
from task import Task as Base
import nidaqmx

class Digital(Base):
  task_type = 'do'
  task_class = nidaqmx.DigitalOutputTask


  def add_channels(self):
    # populate the task with output channels and accumulate the data
    chans = self.channels.items()
    chans.sort( key = lambda v : v[1]['order'] )
    for c,ci in chans:
      debug( 'nidaqmx: creating digital output NIDAQmx channel: %s', c )
      # cut off the prefix
      self.task.create_channel( c.partition('/')[-1] )
