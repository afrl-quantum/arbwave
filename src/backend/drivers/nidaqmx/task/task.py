# vim: ts=2:sw=2:tw=80:nowrap

import copy
from logging import error
from .. import routes
from ....device import Device as Base
from .....signal_graphs import nearest_terminal


class Task(Base):
  task_type = None
  task_class = None

  def __init__(self, device):
    Base.__init__(self, name='{d}/{tt}'.format(d=device,tt=self.task_type))
    self.task = None
    self.channels = None
    self.clocks = None
    self.clock_terminal = None
    self.signals = None

    # first find the possible trigger and clock sources
    self.trig_sources = list()
    self.clock_sources = list()
    self.sources_to_native = dict()

    # make sure the strip off the leading 'ni' but leave the '/'
    clk = str(self)[len(self.prefix()):] + '/SampleClock'
    trg = str(self)[len(self.prefix()):] + '/StartTrigger'

    for i in routes.signal_route_map.items():
      add = False
      if clk == i[1][1]:
        self.clock_sources.append( i[0][0] )
        add = True
      elif trg == i[1][1]:
        self.trig_sources.append( i[0][0] )
        add = True
      if add:
        self.sources_to_native[ i[0][0] ] = i[1][0]

    self.config = self.get_config_template()


  def __del__(self):
    self.clear()


  def clear(self):
    if self.task:
      del self.task
      self.task = None


  def add_channels(self):
    """
    Sub-task types must override this for specific channel creation.
    """
    # populate the task with output channels and accumulate the data
    for c in self.channels:
      self.task.create_channel(c.partition('/')[-1]) # cut off the prefix


  def set_config(self, config=None, channels=None, shortest_paths=None,
                 timing_channels=None, force=False):
    if channels and self.channels != channels:
      self.channels = channels
      force = True
    if config and self.config != config:
      self.config = config
      force = True

    if not self.config['clock']['value']:
      self.clock_terminal = None
    else:
      if shortest_paths:
        self.clock_terminal = \
          self.sources_to_native[
            nearest_terminal( self.config['clock']['value'],
                              set(self.clock_sources),
                              shortest_paths ) ]
        force = True

    if force:
      # rebuild the task
      self.clear()
      self.task = self.task_class()
      self.add_channels()

      # set persistent task properties
      # Not sure if we really need to worry about on-board memory
      # self.task.set_use_only_onboard_memory(
      #   self.config['use-only-onboard-memory']['value'] )


  def set_clocks(self, clocks):
    """
    Implemented by Timing channel
    """
    raise NotImplementedError('only the Timing task can implement clocks')


  def set_output(self, data):
    """
    Sets a static value on each output channel of this task.
    """
    self.task.stop()

    self.task.set_sample_timing( timing_type='on_demand',
                                 mode='finite',
                                 samples_per_channel=1 )
    self.task.configure_trigger_disable_start()
    # get the data
    px = self.prefix()
    chlist = ['{}/{}'.format(px,c) for c in self.task.get_names_of_channels()]
    assert set(chlist) == set( data.keys() ), \
      'NIDAQmx.set_output: mismatched channels'
    self.task.write( [ data[c]  for c in chlist ] )
    self.task.start()


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.
    """
    self.task.stop() # make sure, since static_output must also be stopped
    if not self.clock_terminal:
      raise UserWarning('cannot start waveform without a output clock defined')

    transitions = list(clock_transitions[ self.config['clock']['value'] ])
    transitions.sort()

    # 1.  Sample clock
    if continuous:
      mode = self.config['clock-settings']['mode']['value']
    else:
      mode = 'finite'

    max_clock_rate = self.task.get_sample_clock_max_rate()
    min_dt = 1. / max_clock_rate

    self.task.configure_timing_sample_clock(
      source              = self.clock_terminal,
      rate                = max_clock_rate, # Hz
      active_edge         = self.config['clock-settings']['edge']['value'],
      sample_mode         = mode,
      samples_per_channel = len(transitions) )
    # 2.  Triggering
    if self.config['trigger']['enable']['value']:
      self.task.configure_trigger_digital_edge_start(
        source=self.config['trigger']['source']['value'],
        edge=self.config['trigger']['edge']['value'] )
    else:
      self.task.configure_trigger_disable_start()
    # 3.  Data write
    # 3a.  Get data array
    # loop through each transition and accumulate a list of scans for each
    # channel for each transition.
    # probably need to do some rounding to the nearest clock pulse to ensure
    # that we only have pulses matched to the correct transition

    px = self.prefix()
    chlist = ['{}/{}'.format(px,c) for c in self.task.get_names_of_channels()]
    assert set(chlist).issuperset( waveforms.keys() ), \
      'NIDAQmx.set_output: mismatched channels'

    # get all the waveform data into the scans array.  All remaining None values
    # mean that the prior value for the particular channels(s) should be kept
    # for that scan.
    n_channels = len(chlist)
    scans = dict.fromkeys( transitions )
    nones = [None] * n_channels
    for i in xrange( n_channels ):
      for g in waveforms[ chlist[i] ].items():
        for t,v in g[1]:
          if not scans[t]:
            scans[t] = copy.copy( nones )
          scans[t][i] = v

    # for now, if a channel does not have any data for t=0, we'll issue
    # an error and set the empty channel value at t=0 to zero.
    def zero_if_none(v):
      if v is None:
        error('NIDAQmx: missing starting value for channel--using 0')
        return 0
      else:
        return v
    scans[ transitions[0] ] = [ zero_if_none(v) for v in scans[transitions[0]] ]
    last = scans[ transitions[0] ]
    t_last = -10*min_dt
    for t in transitions:
      if (t - t_last) < min_dt:
        raise RuntimeError('Samples too small for NIDAQmx')
      t_last = t

      t_array = scans[t]
      for i in xrange( n_channels ):
        if t_array[i] is None:
          t_array[i] = last[i]
      last = t_array

    # now, we finally build the actual data to send to the hardware
    scans = [ scans[t]  for t in transitions ]

    # 3b.  Send data to hardware
    self.task.write( scans, auto_start=False, layout='group_by_scan_number' )


  def start(self):
    if self.task:
      self.task.start()


  def stop(self):
    if self.task:
      self.task.stop()


  def get_config_template(self):
    return {
      'use-only-onboard-memory' : {
        'value' : True,
        'type'  : bool,
        'range' : None,
      },
      'trigger' : {
        'enable' : {
          'value' : False,
          'type' : bool,
          'range' : None,
        },
        'source' : {
          'value' : '',
          'type' : str,
          'range' : self.trig_sources,
        },
        'edge' : {
          'value' : 'rising',
          'type' : str,
          'range' : [
            ('falling','Trigger on Falling Edge of Trigger'),
            ('rising', 'Trigger on Rising Edge of Trigger'),
          ],
        },
      },
      'clock' : {
        'value' : '',
        'type' : str,
        'range' : self.clock_sources,
      },
      'clock-settings' : {
        'mode' : {
          'value' : 'continuous',
          'type' : str,
          'range' : [
            ('finite', 'Finite'),
            ('continuous', 'Continuous'),
            ('hwtimed', 'HW Timed Single Point'),
          ],
        },
        'edge' : {
          'value' : 'rising',
          'type' : str,
          'range' : [
            ('falling','Sample on Falling Edge of Trigger'),
            ('rising', 'Sample on Rising Edge of Trigger'),
          ],
        },
      },
    }
