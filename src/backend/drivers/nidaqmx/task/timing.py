# vim: ts=2:sw=2:tw=80:nowrap

from task import Task as Base
import nidaqmx

class Timing(Base):
  task_type = 'to'
  task_class = nidaqmx.CounterOutputTask

  def set_clocks(self, clocks):
    if self.clocks != clocks:
      self.clocks = clocks
      self.set_config( force=True )


  def add_channels(self):
    for c in self.clocks.items():
      self.task.create_channel_frequency(
        c[0], name=c[0],
        idle_state  = c[1]['idle-state'],
        delay       = c[1]['delay'],
        freq        = c[1]['rate'],
        duty_cycle  = c[1]['duty-cycle'],
      )

  def get_config_template(self):
    template = Base.get_config_template(self)
    template.pop('use-only-onboard-memory')
    return template
