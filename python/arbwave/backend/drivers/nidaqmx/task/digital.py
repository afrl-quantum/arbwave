# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
from itertools import chain
import numpy as np
from task import Task as Base
import nidaqmx

class Digital(Base):
  task_type = 'do'
  task_class = nidaqmx.DigitalOutputTask


  def add_channels(self):
    # populate the task with output channels and accumulate the data
    chans = self.channels.items()
    chans.sort( key = lambda v : v[1]['order'] )
    if self.clocks:
      OC = self.onboardclock_name # we ignore the onboard clock
      # add DOTiming clock channels
      chans.extend( (clk,None) for clk in self.clocks if clk != OC )
    for c,ignore in chans:
      debug( 'nidaqmx: creating digital output NIDAQmx channel: %s', c )
      # cut off the prefix
      self.task.create_channel( c.partition('/')[-1] )


  def set_output(self, data):
    OC = self.onboardclock_name
    clocks = self.clocks
    if OC in clocks:
      clocks = clocks.copy()
      clocks.pop(OC) # we ignore the onboard clock for this

    # add the DOTiming clocks with output values...
    if clocks:
      data = data.copy()
      # we just set all DOTiming clock lines to zero for static output
      data.update( { clk:0 for clk in clocks } )
    super(Digital,self).set_output(data)


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.

      waveforms : see gui/plotter/{analog.py,digital.py} for format
      clock_transitions :  dictionary of clocks to dict(ignore,transitions)
      t_max : maximum time of waveforms
    """
    if set(waveforms.keys()).intersection( clock_transitions.keys() ):
      raise RuntimeError('NI channels cannot be used as clocks and ' \
                         'output simultaneously')
    OC = self.onboardclock_name
    clocks = self.clocks
    if OC in clocks:
      clocks = clocks.copy()
      clocks.pop(OC) # we ignore the onboard clock for this

    if clocks:
      # add data for all DOTiming clock lines

      my_dt_clk = clock_transitions[ self.config['clock']['value'] ]['dt']
      waveforms = waveforms.copy()

      for clk, clkcfg in clocks.items():
        this_clock = clock_transitions[clk]
        dt_scale = clkcfg['divider']['value']

        # !!!! THIS CHOICE IS NOT ARBITRARY !!!!
        # This choice is our standard in arbwave.  We require this to be the
        # same as is used in
        # processor.engine.compute._insert_into_parent_clock_transitions
        dt_on = int( dt_scale / 2 )

        transitions = np.array( list( this_clock['transitions'] ), dtype=int )
        transitions.sort()

        Tlist = [((ti, True), (ti+dt_on, False)) for ti in transitions*dt_scale]

        # encoding for clk is step; nidaq only understands step encoding anyway
        waveforms[clk] = { (-1,): ('step', list(chain(*Tlist))) }

    super(Digital,self) \
      .set_waveforms( waveforms, clock_transitions, t_max, continuous)
