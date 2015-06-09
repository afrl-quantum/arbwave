# vim: ts=2:sw=2:tw=80:nowrap

import copy
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
from physical import unit
from .. import ctypes_comedi as c
import numpy as np
from .....tools.signal_graphs import nearest_terminal
from .....tools.cmp import cmpeps
from ....device import Device as Base
from .. import channels


class Subdevice(Base):
  STATIC              = 0
  WAVEFORM_SINGLE     = 1
  WAVEFORM_CONTINUOUS = 2
  subdev_type         = None  # changed by inheriting device types

  def __init__(self, route_loader, device, subdevice, name_uses_subdev=False):
    if name_uses_subdev: devname = '{}{}'.format(self.subdev_type, subdevice)
    else:                devname = 'ao'#self.subdev_type
    name = '{}/{}'.format(device, devname)
    Base.__init__(self, name=name)
    self.base_name = devname
    self.device = device
    self.subdevice = subdevice
    debug( 'loading comedi subdevice %s', self )

    self.task = None
    self.channels = dict()
    self.clocks = None
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0

    # first find the possible trigger and clock sources
    clk = self.name + '/SampleClock'
    trg = self.name + '/StartTrigger'
    if clk not in route_loader.source_map:
      error("No clocks found for clock-able device '%s' (%s)",
            self, self.device.board)
    if trg not in route_loader.source_map:
      error("No triggers found for triggerable device '%s' (%s)", self, self.device.board)
    self.clock_sources = route_loader.source_map[clk]
    self.trig_sources  = route_loader.source_map[trg]
    self.sources_to_native = dict() # not sure if we need this

    self.config = self.get_config_template()
    
    

  def __del__(self):
    self.clear()


  def clear(self):
    if self.task:
      debug( 'comedi: cancelling commands for comedi subdevice %s', self )
      c.comedi_cancel( self.fd, self.subdevice )
      self.t_max = 0.0

  @property
  def fd(self):
    return self.device.fd

  @property
  def prefix(self):
    return self.device.prefix
    
  

  @property
  def flags(self):
    return c.comedi_get_subdevice_flags(self.fd, self.subdevice)

  @property
  def busy(self):
    return self.flags & c.SDF_BUSY

  @property
  def running(self):
    return self.flags & c.SDF_RUNNING

  #@property
  def status(self):
    flags = self.flags
    D = dict(
      busy                  =     bool(flags & c.SDF_BUSY),
      busy_owner            =     bool(flags & c.SDF_BUSY_OWNER),
      locked                =     bool(flags & c.SDF_LOCKED),
      lock_owner            =     bool(flags & c.SDF_LOCK_OWNER),
      maxdata_per_channel   =     bool(flags & c.SDF_MAXDATA),
      flags_per_channel     =     bool(flags & c.SDF_FLAGS),
      rangetype_per_channel =     bool(flags & c.SDF_RANGETYPE),
      async_cmd_supported   =     bool(flags & c.SDF_CMD),
      soft_calibrated       =     bool(flags & c.SDF_SOFT_CALIBRATED),
      readable              =     bool(flags & c.SDF_READABLE),
      writeable             =     bool(flags & c.SDF_WRITEABLE),
      internal              =     bool(flags & c.SDF_INTERNAL),
      aref_ground_supported =     bool(flags & c.SDF_GROUND),
      aref_common_supported =     bool(flags & c.SDF_COMMON),
      aref_diff_supported   =     bool(flags & c.SDF_DIFF),
      aref_other_supported  =     bool(flags & c.SDF_OTHER),
      dither_supported      =     bool(flags & c.SDF_DITHER),
      deglitch_supported    =     bool(flags & c.SDF_DEGLITCH),
      running               =     bool(flags & c.SDF_RUNNING),
      sample_32bit          =     bool(flags & c.SDF_LSAMPL),
      sample_16bit          = not bool(flags & c.SDF_LSAMPL),
      sample_bitwise        =     bool(flags & c.SDF_PACKED),
    )
    #D.__dict__ = D
    return D

  @property
  def available_channels(self):
    klass = channels.klasses[self.subdev_type]
    return [
      klass('{}/{}'.format(self, i), self)
      for i in xrange(c.comedi_get_n_channels( self.fd, self.subdevice ))
    ]

  def add_channels(self):
    """
    Sub-task types must override this for specific channel creation.
    """
    # populate the task with output channels and accumulate the data
    for c in self.channels:
      warn( 'creating unknown NIDAQmx task/channel: %s/%s', self.task, c )
      self.task.create_channel(c.partition('/')[-1]) # cut off the prefix


  def set_config(self, config=None, channels=None, shortest_paths=None,
                 timing_channels=None, force=False):
    debug('comedi[%s].set_config', self)
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
    Implemented by Timing channel
    """
    raise NotImplementedError('only the Timing task can implement clocks')


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
    if self.task and self.channels:
      # this is kind of hackish and might be wrong for other hardware (that is
      # not the PCI-6723).  The PCI-6723 did not like having < 1*..., therefore
      # we use max(1, .6*...).
      return max( 1, .6*len(self.channels) ) \
            * unit.s / self.task.get_sample_clock_max_rate()
    return 0*unit.s


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.
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

    # 1.  Sample clock
    if continuous:
      mode = self.config['clock-settings']['mode']['value']
    else:
      mode = 'finite'

    max_clock_rate = self.task.get_sample_clock_max_rate()
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
        max_clock_rate,
        self.config['clock-settings']['edge']['value'],
        mode,
        len(transitions),
      )
    self.task.configure_timing_sample_clock(
      source              = self.clock_terminal,
      rate                = max_clock_rate, # Hz
      active_edge         = self.config['clock-settings']['edge']['value'],
      sample_mode         = mode,
      samples_per_channel = len(transitions) )
    # 2.  Triggering
    if self.config['trigger']['enable']['value']:
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
      'NIDAQmx.set_output: mismatched channels'

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
