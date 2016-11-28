# vim: ts=2:sw=2:tw=80:nowrap

import copy
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
from ....device import Device as Base
from .....tools.signal_graphs import nearest_terminal
from .....tools.cmp import cmpeps
from .....tools import cached
from physical import unit
import nidaqmx
import numpy as np


class Task(Base):
  task_type = None
  task_class = None
  STATIC              = 0
  WAVEFORM_SINGLE     = 1
  WAVEFORM_CONTINUOUS = 2
  finite_end_clock = False # whether this task requires end-clock (see analog.py)

  def __init__(self, driver, device):
    Base.__init__(self, name='{d}/{tt}'.format(d=device,tt=self.task_type))
    self.task = None
    self.channels = dict()
    self.clocks = dict()
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0

    # first find the possible trigger and clock sources
    self.trig_sources = list()
    self.clock_sources = list()
    self.SCTB_sources = list()
    self.sources_to_native = dict()

    # make sure the strip off the leading 'ni' but leave the '/'
    clk = self.format_ni_terminal_name('SampleClock')
    trg = self.format_ni_terminal_name('StartTrigger')
    sctb= self.format_ni_terminal_name('SampleClockTimebase')

    lD = {clk:self.clock_sources, trg:self.trig_sources, sctb:self.SCTB_sources}

    for i in driver.rl.signal_route_map.items():
      l = lD.get( i[1][1], None )
      if l is not None:
        l.append( i[0][0] )
        self.sources_to_native[ i[0][0] ] = i[1][0]

    self.config = self.get_config_template()


  def __del__(self):
    self.clear()


  def clear(self):
    if self.task:
      debug( 'nidaqmx: clearing NIDAQmx task %s', self.task )
      del self.task
      self.task = None
      self.t_max = 0.0

  def format_ni_terminal_name(self, terminal):
    return self.name[len(self.prefix):] + '/' + terminal

  def add_channels(self):
    """
    Sub-task types must override this for specific channel creation.
    """
    # populate the task with output channels and accumulate the data
    for c in self.channels:
      warn( 'creating unknown NIDAQmx task/channel: %s/%s', self.task, c )
      self.task.create_channel(c.partition('/')[-1]) # cut off the prefix

  @cached.property
  def has_onboardclock(self):
    return self.onboardclock_name in self.clock_sources

  @cached.property
  def onboardclock_name(self):
    return self.name + '/' + 'SampleClock'

  def set_config(self, config=None, channels=None, signal_graph=None):
    do_rebuild = False
    if channels and self.channels != channels:
      self.channels = channels
      do_rebuild = True
    if config and self.config != config:
      self.config = config
      do_rebuild = True

    if not self.config['clock']['value']:
      self.clock_terminal = None
    else:
      if signal_graph:
        if self.config['clock']['value'] == self.onboardclock_name:
          # don't have to lookup anymore, since we know it is already the
          # onboard clock
          self.clock_terminal = 'OnboardClock'
        else:
          self.clock_terminal = \
            self.sources_to_native[
              nearest_terminal( self.config['clock']['value'],
                                set(self.clock_sources),
                                signal_graph ) ]
        do_rebuild = True

    if do_rebuild:
      self._rebuild_task()

  def _rebuild_task(self):
    # rebuild the task
    self.clear()
    if not self.channels:
      return
    debug( 'nidaqmx: creating task:  %s', self.name )
    self.task = self.task_class(self.name.replace('/','-'))
    self.use_case = None
    self.add_channels()

    # set persistent task properties
    # Not sure if we really need to worry about on-board memory
    # self.task.set_use_only_onboard_memory(
    #   self.config['use-only-onboard-memory']['value'] )


  def set_clocks(self, clocks):
    """
    If this is an analog device, this must be the onboard clock only.
    If this is a digital device, either an Onboard timer for the digital device
    (if supported) or aperiodic clock implemented by a digital line of a digital
    device.
    If this is a timing device, this must be one of the counters.
    """
    if self.clocks != clocks:
      self.clocks = clocks


  def set_output(self, data):
    """
    Sets a static value on each output channel of this task.
    """
    if self.use_case in [ None, Task.STATIC ]:
      if self.use_case is not None:
        debug( 'nidaqmx: stopping task: %s', self.task )
        self.task.stop()
    else:
      self._rebuild_task()
    self.use_case = Task.STATIC

    debug( 'nidaqmx: configuring task for static output: %s', self.task )
    self.task.set_sample_timing( timing_type='on_demand',
                                 mode='finite',
                                 samples_per_channel=1 )
    if self.trig_sources:
      # this device _does_ accept triggers
      self.task.configure_trigger_disable_start()
    # get the data
    px = self.prefix
    chlist = ['{}/{}'.format(px,c) for c in self.task.get_names_of_channels()]
    assert set(chlist) == set( data.keys() ), \
      'NIDAQmx.set_output: mismatched channels'
    debug( 'nidaqmx: writing static data for channels: %s', chlist )
    if rootlog.getEffectiveLevel() <= (DEBUG-1):
      log(DEBUG-1, '%s', [ float(data[c])  for c in chlist ])
    self.task.write( [ data[c]  for c in chlist ] )
    debug( 'nidaqmx: starting task: %s', self.task )
    self.task.start()


  def get_min_period(self):
    if self.has_onboardclock and self.task and self.channels:
      return unit.s / self.task.get_sample_clock_max_rate()
    return 0*unit.s


  def get_clock_rate(self):
    if not self.has_onboardclock:
      # It seems that if a device does not have an onboard clock, the call to
      # get_sample_clock_max_rate fails.
      # If this is ever an analog output device, this will probably fail since
      # the max-rate must be specified to program the DAC settling time.
      return 0
    if self.clock_terminal == 'OnboardClock':
      return self.clocks[ self.onboardclock_name ]['rate']['value']
    return self.task.get_sample_clock_max_rate()


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.

      waveforms : see gui/plotter/digital.py for format
      clock_transitions :  dictionary of clocks to dict(ignore,transitions)
      t_max : maximum time of waveforms
    """
    if self.use_case in [None, Task.WAVEFORM_SINGLE, Task.WAVEFORM_CONTINUOUS]:
      if self.use_case is not None:
        debug( 'nidaqmx: stopping task: %s', self.task )
        self.task.stop()
    else:
      self._rebuild_task()
    if continuous:
      self.use_case = Task.WAVEFORM_CONTINUOUS
    else:
      self.use_case = Task.WAVEFORM_SINGLE

    if not self.clock_terminal:
      raise UserWarning('cannot start waveform without a output clock defined')


    my_clock = clock_transitions[ self.config['clock']['value'] ]
    dt_clk = my_clock['dt']
    transitions = list( my_clock['transitions'] )
    transitions.sort()

    if self.finite_end_clock and not continuous:
      # This task requires an additional clock pulse at the end of the sequence
      # in order for the hardware to properly notify the software of completion.
      # It is the responsibility of each driver to ensure that the last clock
      # transitions is ignored if the driver has already indicated to arbwave
      # that an extra clock pulse is required.
      transitions = transitions[:-1]

    # 1.  Sample clock
    if continuous:
      mode = self.config['clock-settings']['mode']['value']
    else:
      mode = 'finite'

    clock_rate = self.get_clock_rate()
    min_dt = self.get_min_period().coeff

    debug( 'nidaqmx: configuring task timing for waveform output: %s', self.task )
    if rootlog.getEffectiveLevel() <= (DEBUG-1):
      log(DEBUG-1,'self.task.configure_timing_sample_clock('
        'source'           '=%s,'
        'rate'             '=%s Hz,'
        'active_edge'      '=%s,'
        'sample_mode'      '=%s,'
        'samples_per_channel=%s)',
        self.clock_terminal,
        clock_rate,
        self.config['clock-settings']['edge']['value'],
        mode,
        len(transitions),
      )
    self.task.configure_timing_sample_clock(
      source              = self.clock_terminal,
      rate                = clock_rate, # Hz
      active_edge         = self.config['clock-settings']['edge']['value'],
      sample_mode         = mode,
      samples_per_channel = len(transitions) )
    # 2.  Triggering
    if not self.trig_sources:
      pass # this device does not accept triggers
    elif self.config['trigger']['enable']['value']:
      debug( 'nidaqmx: configuring task trigger for waveform output: %s', self.task )
      if rootlog.getEffectiveLevel() <= (DEBUG-1):
        log(DEBUG-1, 'self.task.configure_trigger_digital_edge_start('
          'source=%s,edge=%s)',
          self.config['trigger']['source']['value'],
          self.config['trigger']['edge']['value'],
        )
      self.task.configure_trigger_digital_edge_start(
        source=self.config['trigger']['source']['value'],
        edge=self.config['trigger']['edge']['value'] )
    else:
      debug('nidaqmx: disabling trigger start for task: %s', self.task)
      self.task.configure_trigger_disable_start()
    # 3.  Data write
    # 3a.  Get data array
    # loop through each transition and accumulate a list of scans for each
    # channel for each transition.
    # probably need to do some rounding to the nearest clock pulse to ensure
    # that we only have pulses matched to the correct transition

    px = self.prefix
    chlist = ['{}/{}'.format(px,c) for c in self.task.get_names_of_channels()]
    assert set(chlist).issuperset( waveforms.keys() ), \
      'NIDAQmx.set_waveforms: mismatched channels'

    # get all the waveform data into the scans array.  All remaining None values
    # mean that the prior value for the particular channels(s) should be kept
    # for that scan.
    n_channels = len(chlist)
    scans = dict.fromkeys( transitions )
    nones = [None] * n_channels
    for i in xrange( n_channels ):
      if chlist[i] not in waveforms:
        continue
      for g in waveforms[ chlist[i] ].items():
        for t,v in g[1]:
          if not scans[t]:
            scans[t] = copy.copy( nones )
          scans[t][i] = v

    # for now, if a channel does not have any data for t=0, we'll issue
    # an error and set the empty channel value at t=0 to zero.
    def zero_if_none(v, channel):
      if v is None:
        warn('NIDAQmx: missing starting value for channel (%s)--using 0',
             chlist[channel])
        return 0
      else:
        return v

    S0 = scans[ transitions[0] ]
    if S0 is None:
      # must be sharing a clock with another card.  init all channels to zero
      last = scans[ transitions[0] ] = [0] * n_channels
    else:
      scans[ transitions[0] ] = [
        zero_if_none(v,i) for v,i in zip( S0, xrange(len(S0)) )
      ]
      last = scans[ transitions[0] ]

    if len(transitions) > 1:
      # NI seems to have problems with only one transition any way, but...
      diff_transitions = np.diff( transitions )
      min_transition = np.argmin( diff_transitions )
      if diff_transitions[min_transition] < round(min_dt/dt_clk):
        raise RuntimeError(
          '{name}: Samples too small for NIDAQmx at t={tl}->{t}: {dt}<({m}/{clk})'
          .format(name=self.name,
                  tl=transitions[min_transition],
                  t=transitions[min_transition+1],
                  dt=diff_transitions[min_transition],
                  m=min_dt, clk=dt_clk)
        )

    for t in transitions:
      t_array = scans[t]
      if t_array is None:
        # must be sharing a clock with another card.  keep last values
        scans[t] = last
      else:
        for i in xrange( n_channels ):
          if t_array[i] is None:
            t_array[i] = last[i]
        last = t_array

    # now, we finally build the actual data to send to the hardware
    scans = [ scans[t]  for t in transitions ]

    # 3b.  Send data to hardware
    debug( 'nidaqmx: writing waveform data for channels: %s', chlist )
    debug( 'nidaqmx: NIDAQmx len(transitions/in) = %s, len(scans/out) = %s',
           len(transitions), len(scans) )
    if rootlog.getEffectiveLevel() <= (DEBUG-1):
      log(DEBUG-1, 'NIDAQmx task.write(<data>, False, group_by_scan_number)' )
      log(DEBUG-1, '<data>:' )
      for scan in scans:
        log(DEBUG-1, '          %s', np.array(scan).astype(float).tolist())
    self.task.write( scans, auto_start=False, layout='group_by_scan_number' )
    self.t_max = t_max


  def start(self):
    if self.task:
      self.task.start()


  def wait(self):
    if self.task:
      log(DEBUG-1,'NIDAQmx: waiting for task (%s) to finish...', self.task)
      log(DEBUG-1,'NIDAQmx:  already done? %s', self.task.is_done())
      if self.use_case == Task.WAVEFORM_CONTINUOUS:
        raise RuntimeError('Cannot wait for continuous waveform tasks')
      try: self.task.wait_until_done( timeout = self.t_max*2 )
      except nidaqmx.libnidaqmx.NIDAQmxRuntimeError, e:
        debug('NIDAQmx:  task.wait() timed out! finished=%s',
              self.task.is_done())
      log(DEBUG-1,'NIDAQmx: task (%s) finished', self.task)


  def stop(self):
    if self.task:
      self.task.stop()


  def get_config_template(self):
    C = {
      'use-only-onboard-memory' : {
        'value' : True,
        'type'  : bool,
        'range' : None,
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
        'Timebase' : {
          'clock' : {
            'value' : '', #FIXME:  what should the default be? MasterTimebase?
            'type' : str,
            'range' : self.SCTB_sources,
          },
        },
      },
    }

    if self.trig_sources:
      C.update(
        trigger  = {
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
      )
    return C
