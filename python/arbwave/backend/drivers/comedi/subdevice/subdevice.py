# vim: ts=2:sw=2:tw=80:nowrap

import copy, time, re
from mmap import mmap, PROT_WRITE, MAP_SHARED
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
import numpy as np
import ctypes
from ctypes import memset, sizeof, byref
from itertools import izip

from physical import unit

import comedi

from .....tools.signal_graphs import nearest_terminal
from .....tools.cmp import cmpeps
from .....tools import cached
from ....device import Device as Base
from .. import channels
from . import capabilities


command_test_errors = {
  1: 'unsupported trigger in ..._src setting of comedi command, setting zeroed',
  2: '..._src setting not supported by driver',
  3: 'TRIG argument of comedi command outside accepted range',
  4: 'adjusted TRIG argument in comedi command',
  5: 'chanlist not supported by board',
}



def raiserr(retval, msg='', exception=OSError):
  if retval < 0:
    err = comedi.errno()
    raise exception('comedi, {},{}/{}: {}'.format(msg,retval,err,comedi.strerror(err)))

class Subdevice(Base):
  """
  In the context of Arbwave, a comedi subdevice is actually a represetation of
  what Arbwave considers to be a self-contained device.
  """

  subdev_type         = None  # changed by inheriting device types
  units               = comedi.UNIT_volt
  default_range_min   = 0
  default_range_max   = 1

  def __init__(self, card, subdevice, name_uses_subdev=False):
    """
    parameter:  name_uses_subdev
      If there are more than one device on this card that performs the same
      function, such as two analog output devices (which get separately clocked,
      triggered, ...), then we want the name of those devices to also use the
      number of the subdevice.  But, when there is only one device of a certain
      type on the card, we simply use the subdev_type as the main part of the
      name.  For instance, if it is an analog output device and there is only
      one on the "0" card, the name of the device would be "comedi/0/ao"
      whereas, if there were two analog output devices on the card, the names
      would be "comedi/0/ao1" and "comedi/0/ao2".
    """
    if name_uses_subdev: devname = '{}{}'.format(self.subdev_type, subdevice)
    else:                devname = self.subdev_type

    super(Subdevice,self).__init__(name='{}/{}'.format(card, devname))
    self.card = card
    self.subdevice = subdevice
    debug( 'loading comedi subdevice %s', self )
    self.channels = dict()
    self.clocks = dict()
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0
    self.cmd = comedi.cmd()
    self.cmd_chanlist = None

    # lets get the src mask to see if we are always required to do internal
    # trigger.  We are assuming that if a command cannot be started with
    # TRIG_NOW, it must require some sort of two part setup regardless of
    # whether it uses TRIG_INT or TRIG_EXT.  The NI cards are this way
    # explicitly so that DMA transfers get primed--comedi.internal_trigger must
    # be used whether we use TRIG_INT or TRIG_EXT.  For the case of TRIG_EXT, it
    # will just wait for the actual trigger.
    comedi.get_cmd_src_mask(card, subdevice, self.cmd)
    self.trig_now_supported = bool( self.cmd.start_src & comedi.TRIG_NOW )
    memset( byref(self.cmd), 0, sizeof(self.cmd) )

    sd_flags = self.status()
    self.sampl_t = comedi.sampl_t if sd_flags.sample_16bit else comedi.lsampl_t

    assert not sd_flags.flags_per_channel, 'flags per channel!'

    size = comedi.get_buffer_size( self.card, self.subdevice )
    # The c version; we can cast directly
    #data = mmap(NULL, size, PROT_WRITE, MAP_SHARED, comedi.fileno(dev), 0)

    # Set the current write device so that the mmap will be correct
    comedi.set_write_subdevice( self.card, self.subdevice )

    # the python version;  we must cast using ctypes/numpy
    self.mapped = mmap( comedi.fileno(self.card), size,
                        prot=PROT_WRITE, flags=MAP_SHARED, offset=0 )
    if not self.mapped:
      raise OSError( 'mmap: error!' ) # probably will already be raised

    memory = np.ndarray( shape=(size,), dtype=ctypes.c_ubyte,
                         buffer=self.mapped, order='C' )
    memory[:] = 0 # zero the buffer to begin

    # create and easy lookup from destination to list of sources
    dst_to_src = dict()
    for src,dst in self.card.available_routes:
      D = dst_to_src.setdefault(dst, list())
      D.append(src)

    #first find the possible trigger and clock sources
    clk = self.name + '/SampleClock'
    trg = self.name + '/StartTrigger'

    self.clock_sources = dst_to_src.get(clk, list())
    self.trig_sources  = dst_to_src.get(trg, list())
    self.clock_sources.sort()
    self.trig_sources.sort()

    if not self.clock_sources:
      error("No clocks found for clock-able device '%s' (%s)",
            self, self.card.board)
    else:
      self.config_template['clock']['range'] = self.clock_sources

    if not self.trig_sources:
      # internal trigger only
      self.config_template = self.config_template.copy()
      self.config_template.pop('trigger')
    else:
      self.config_template['trigger']['source']['range'] = self.trig_sources

    self.config = self.get_config_template()


  def __del__(self):
    self.clear()

  def clear(self):
    debug( 'comedi: cancelling commands for comedi subdevice %s', self )
    raiserr( comedi.cancel( self.card, self.subdevice ), 'cancel' )
    self.t_max = 0.0
    memset( byref(self.cmd), 0, sizeof(self.cmd) )
    del self.cmd_chanlist
    self.cmd_chanlist = None


  def get_config(self, L):
    """
    Simple accessor for configuration items.  This is primarily used so that
    subclasses can have different names, or even static values, for similar
    config concepts.
    """
    if type(L) not in [list, tuple]:
      return L

    C = self.config
    for li in L:
      C = C[li]
    return C

  @cached.property
  def has_onboardclock(self):
    return self.onboardclock_name in self.clock_sources

  @cached.property
  def onboardclock_name(self):
    return self.card.signal_names['onboardclock'].format(dev=self.name)

  @property
  def flags(self):
    return comedi.get_subdevice_flags(self.card, self.subdevice)

  @property
  def busy(self):
    return bool( self.flags & comedi.SDF_BUSY )

  @property
  def running(self):
    return bool( self.flags & comedi.SDF_RUNNING )

  @property
  def buf_size(self):
    return comedi.get_buffer_size(self.card, self.subdevice)

  #@property
  def status(self):
    return comedi.extensions.subdev_flags.to_dict( self.flags )

  @property
  def available_channels(self):
    klass = channels.klasses[self.subdev_type]

    return [
      klass('{}{}'.format(self, i), self)
      for i in xrange(comedi.get_n_channels( self.card, self.subdevice ))
    ]


  def config_all_channels(self):
    """
    Configure all channels and return them.

    Actually just calls self._config_all_channels(self.channels)
    """
    return self._config_all_channels( dict(self.channels, **self.clocks) )


  def _config_all_channels(self, channels):
    """
    Configure all given channels and return them.
    """
    dflt_mn = self.get_config( self.default_range_min )
    dflt_mx = self.get_config( self.default_range_max )

    self.ranges = dict()
    self.maxdata = dict()
    C, S = self.card, self.subdevice
    for chname, chinfo in channels.items():
      mx = chinfo.get('max', dflt_mx)
      mn = chinfo.get('min', dflt_mn)
      ch = self.get_channel(chname)

      self.ranges[chname]=r=comedi.find_range(C, S, ch, self.units, mn, mx)
      self.maxdata[chname]= comedi.get_maxdata(C, S, ch)

      assert r >= 0, 'comedi: Could not identify output range for '+chname

      # if self.ranges[chname] >= 0:
      #   continue

      # simple find did not work, try harder (?)
      #ch_ranges = [
      #  ( i, comedi.get_range(C, S, ch, i) )
      #  for i in xrange( comedi.get_n_ranges( C, S, ch ) )
      #]

      #ch_ranges.sort(key = lambda ri : ri[1].contents.max - ri[1].contents.min)
    return channels



  def cmd_is_continuous(self):
    """
    Tests the comedi.cmd to see if it was configured for continuous mode.
    """
    return self.cmd.stop_src == comedi.TRIG_NONE


  def set_config(self, config=None, channels=None, signal_graph=None):
    debug('comedi[%s].set_config', self)

    if channels is not None and self.channels != channels:
      self.channels = channels
    if config is not None and self.config != config:
      self.config = config

    if not self.config['clock']['value']:
      self.clock_terminal = None
    else:
      if signal_graph:
        if self.has_onboardclock and \
           self.config['clock']['value'] == self.onboardclock_name:
          # don't have to lookup anymore, since we know it is already the
          # onboard clock
          self.clock_terminal = 'internal'
        else:
          self.clock_terminal = \
              nearest_terminal( self.config['clock']['value'],
                                  set(self.clock_sources),
                                  signal_graph )

    if self.clock_terminal == 'internal':
      frequency = self.clocks[ self.onboardclock_name ]['rate']['value']
      clock_args   = (comedi.TRIG_TIMER, int(1e9 / frequency))
    else:
      channel = self.card.name_table[self.clock_terminal]
      invert = 0
      if config['clock-edge']['value'] == 'falling':
        invert = comedi.CR_INVERT
      clock_args = (comedi.TRIG_EXT,
                    comedi.CR_PACK_FLAGS(channel, 0, 0, comedi.CR_EDGE | invert))

    trigger_args = ( comedi.TRIG_INT, 0 )
    if 'trigger' in self.config and self.config['trigger']['enable']['value']:
      channel = self.card.name_table[self.clock_terminal]
      invert = 0
      if self.config['trigger']['edge']['value'] == 'falling':
        invert = comedi.CR_INVERT
      trigger_args = (comedi.TRIG_EXT,
                      comedi.CR_PACK_FLAGS(channel, 0, 0, comedi.CR_EDGE | invert))



    # NOW WE ARE READY TO ACTUAL CONFIGURE...
    # start with a clean slate:
    self.clear()

    debug('comedi: creating command:  %s', self.name)

    #### Now set self.cmd ####
    channels = self.config_all_channels().items()
    channels.sort( key = lambda i : i[1]['order'] )
    self.cmd_chanlist = create_chanlist(self.cr_pack, channels)

    self.cmd.subdev         = self.subdevice
    self.cmd.flags          = comedi.TRIG_WRITE #bitwise or'd subdevice flags
    self.cmd.chanlist       = self.cmd_chanlist
    self.cmd.chanlist_len   = len( self.cmd_chanlist )
    self.cmd.start_src      = trigger_args[0]
    self.cmd.start_arg      = trigger_args[1]
    self.cmd.scan_begin_src = clock_args[0]
    self.cmd.scan_begin_arg = clock_args[1]
    self.cmd.convert_src    = comedi.TRIG_NOW # accpets: TRIG_TIMER, TRIG_EXT, TRIG_NOW
    self.cmd.convert_arg    = 0
    self.cmd.scan_end_src   = comedi.TRIG_COUNT
    self.cmd.scan_end_arg   = len( self.cmd_chanlist ) # iterate through all channels
    self.cmd.stop_src       = comedi.TRIG_COUNT # accepts: TRIG_COUNT, TRIG_NONE
    self.cmd.stop_arg       = 0 # we'll set src/arg at the time of set_waveforms
    #### finished init of self.cmd ####

    #### testing cmd ####
    err = comedi.command_test(self.card, self.cmd)
    if err in [1, 2, 3, 5]:
      raise RuntimeError('comedi[{}]: ' + command_test_errors[err])
    if err == 4:
      warn('comedi[%s]: %s', self, command_test_errors[err])


  def set_clocks(self, clocks):
    """
    If this is an analog device, this must be the onboard clock only.
    If this is a digital device, either an Onboard timer for the digital device
    (if supported) or aperiodic clock implemented by a digital line of a digital
    device.  If this is a timing device, this must be one of the counters.
    """
    if self.clocks != clocks:
      self.clocks = clocks


  def get_channel(self, name):
    return int( re.search(self.subdev_type + '([0-9]*)$', name).group(1) )


  def convert_data(self, chname, data):
    """
    Takes data in physical units and converts it to (l)sampl_t data that comedi
    needs.

    This allows for arrays of data to be converted.
    """
    #return comedi.from_phys(data,self.ranges[chname],self.maxdata[chname])
    # implement comedi.from_phys here so that we can use arrays
    rng = comedi.get_range(
            self.card, self.subdevice,
            self.get_channel(chname), self.ranges[chname] ).contents
    maxdata = self.maxdata[chname]
    return np.clip(           (data - rng.min*unit.V) *
                    (maxdata / ( rng.max - rng.min ) / unit.V),
                   0, maxdata ).astype( self.sampl_t )


  def cr_pack(self, chname, chinfo):
    """
    Packs data properly whether this is digital or analog
    """
    return comedi.CR_PACK(
      self.get_channel(chname),
      self.ranges[chname],
      self.get_config(self.reference_value),
    )


  def set_output(self, data):
    """
    Sets a static value on each output channel of this task.
    """
    return self._set_output(data, self.channels)

  def _set_output(self, data, channels):
    """
    Sets a static value on each output channel of this task.

    This version allows the caller to add items to the channel list.
    """
    data = data.items()
    data.sort( key = lambda i : channels[i[0]]['order'] )

    insn_list = comedi.insnlist()
    insn_list.set_length( len(data) )
    # we allocate the data to ensure it does not get garbage collected too soon
    L = [ comedi.lsampl_t() for i in xrange( len(data) ) ]

    for i, (chname, value), di in izip( insn_list, data, L ):
      di.value = self.convert_data( chname, value )

      i.insn = comedi.INSN_WRITE
      i.subdev = self.subdevice
      i.chanspec = self.cr_pack(chname, channels[chname])
      i.n = 1
      i.data = ctypes.pointer( di )
    n = comedi.do_insnlist( self.card, insn_list )
    raiserr( n - len(data), 'insnlist not complete' )


  def get_min_period(self):
    #important function for Arbwave to use clocks
    #below is effective for timing subdevices
    #getting a period of a non-subdevice signal will need a dictionary with their period

    if self.subdev_type == 'to':
      chan = 0 #I think this is what we want
      clock = ctypes.c_uint()
      period = ctypes.c_uint()
      ret = comedi.get_clock_source(self.card, self.subdevice, chan, clock,
                                    period)
      raiserr(ret, 'get_clock_source')
      print self.subdevice, "timing device"
      return int(period.value)*unit.ns
    else:
      # we use the new comedi facility to query async subdevice speeds
      scan_begin_min, convert_min = ctypes.c_uint(), ctypes.c_uint()
      retval = comedi.get_cmd_timing_constraints(self.card, self.subdevice,
            self.cmd.scan_begin_src, byref(scan_begin_min),
            self.cmd.convert_src,    byref(convert_min),
            self.cmd.chanlist, self.cmd.chanlist_len)
      if retval < 0:
        raise RuntimeError(
          'comedi.get_min_period: '
          'get_cmd_timing_constraints({}, subdev={}, scan_src={}, <addr>, '
          'convert_src={}, <addr>, <addr>, chlen={}) failed (=={})'
          .format(self.card, self.subdevice, self.cmd.scan_begin_src,
                  self.cmd.convert_src, self.cmd.chanlist_len, retval)
        )
      return scan_begin_min.value*unit.ns

  @cached.property
  def finite_end_clock(self):
    C = capabilities.get(self.card.kernel, self.card.board, self.subdev_type)
    return C['finite_end_clock']

  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.
    """
    S = self.status()
    assert not S.sample_bitwise, 'Please implement Bitwise cmd data'

    if not self.clock_terminal:
      raise UserWarning('cannot start waveform without an output clock defined')

    my_clock = clock_transitions[ self.config['clock']['value'] ]
    dt_clk = my_clock['dt']
    transitions = list( my_clock['transitions'] )
    transitions.sort()

    if self.finite_end_clock and not continuous:
      # This subdevice requires an additional clock pulse at the end of the
      # sequence in order for the hardware to properly notify the software of
      # completion.  It is the responsibility of each driver to ensure that the
      # last clock transitions is ignored if the driver has already indicated to
      # arbwave that an extra clock pulse is required.
      transitions = transitions[:-1]



    # 1. Set (non)continuous mode and number of samples per channel

    # Set output to either continuous or one-time
    self.cmd.stop_src = comedi.TRIG_NONE if continuous else comedi.TRIG_COUNT

    # should be samples_per_channel
    self.cmd.stop_arg = len(transitions)



    # 3.  Data write
    # 3a.  Get data array
    # loop through each transition and accumulate a list of scans for each
    # channel for each transition.
    # probably need to do some rounding to the nearest clock pulse to ensure
    # that we only have pulses matched to the correct transition

    chlist = [ '{}{}'.format(self, comedi.CR_CHAN(ch_info))
      for ch_info in self.cmd_chanlist
    ]

    assert set(chlist).issuperset( waveforms.keys() ), \
      'comedi.set_waveforms: mismatched channels'

    # get all the waveform data into the scans array.  All remaining None values
    # mean that the prior value for the particular channels(s) should be kept
    # for that scan.
    n_channels = len(self.cmd_chanlist)

    if n_channels == 0:
      debug('comedi:  no channels for waveform output')
      return

    scans = dict.fromkeys( transitions )
    nones = [None] * n_channels
    for i in xrange( n_channels ):
      if chlist[i] not in waveforms:
        continue
      for wf_path, (encoding,group_trans) in waveforms[ chlist[i] ].iteritems():
        assert encoding == 'step', \
          'non-step transition encoding for comedi: '+encoding
        for timestamp, value in group_trans:
          if not scans[timestamp]:
            scans[timestamp] = copy.copy( nones )
          scans[timestamp][i] = value

    # for now, if a channel does not have any data for t=0, we'll issue
    # an error and set the empty channel value at t=0 to zero.
    def zero_if_none(v, channel):
      if v is None:
        warn('comedi: missing starting value for channel (%s)--using 0',
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
        zero_if_none(v,i) for v,i in izip( S0, xrange(len(S0)) )
      ]
      last = scans[ transitions[0] ]

    min_dt = self.get_min_period().coeff

    if len(transitions) > 1:
      # NI seems to have problems with only one transition any way, but...
      diff_transitions = np.diff( transitions )
      min_transition = np.argmin( diff_transitions )
      if diff_transitions[min_transition] < round(min_dt/dt_clk):
        raise RuntimeError(
          '{name}: Samples too small for comedi at t={tl}->{t}: {dt}<({m}/{clk})'
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
    scans = np.array([ scans[t]  for t in transitions ])

    # 3b.  Send data to hardware
    debug( 'comedi: writing waveform data for channels: %s', chlist )
    debug( 'comedi: len(transitions/in) = %s, len(scans/out) = %s',
           len(transitions), len(scans) )
    if rootlog.getEffectiveLevel() <= (DEBUG-1):
      log(DEBUG-1, 'comedi: mmap.write(<data>)' )
      log(DEBUG-1, '<data>:' )
      for scan in scans:
        log(DEBUG-1, '          %s', np.array(scan).astype(float).tolist())

    shape = ( len(transitions), len(self.cmd_chanlist) )
    data = np.ndarray( shape=shape, dtype=self.sampl_t,
                       buffer=self.mapped, order='C' )

    # this writes it to kernel memory
    # FIXME:  this might not be right; might also exist much faster operation
    # for this
    #data[:] = scans
    # scale the data to sampl type.
    for ch_i, ch in zip(xrange(n_channels), chlist):
      data[:,ch_i] = self.convert_data( ch, scans[:,ch_i] )

    self.t_max = t_max


  def start(self):
    if not self.busy and len(self.cmd_chanlist) > 0:
      # 1. Start the command
      err = comedi.command(self.card, self.cmd)
      raiserr(err)
      # 2. Mark the already written buffer as written
      # we have to mark this now, since comedi.command resets all the buffer
      # counters.
      output_size = self.cmd.stop_arg * self.cmd.chanlist_len \
                  * sizeof(self.sampl_t)
      m = comedi.mark_buffer_written( self.card, self.cmd.subdev,
                                           output_size )
      raiserr(m,'mark_buffer')
      if m != output_size:
        raise OSError('comedi: could not mark entire buffer')

      # 3. trigger
      self.trigger()


  def trigger(self):
    if (not self.trig_now_supported) or self.cmd.start_src == comedi.TRIG_INT:
      debug('comedi: sending internal trigger signal')
      ret = comedi.internal_trigger(self.card, self.subdevice, 0)
      raiserr(ret, 'internal_trigger')
    else:
      debug('comedi: waiting for external trigger')



  def wait(self):
    if self.busy:
      log(DEBUG-1,'comedi: waiting for (%s) to finish...', self)
      if self.cmd_is_continuous():
        raise RuntimeError('Cannot wait for continuous waveform tasks')

      timeout = self.t_max*2
      t0 = time.time()
      while self.running:
        t1 = time.time()
        if (t1 - t0) > timeout:
          raise RuntimeError('timed out waiting for comedi command {}'.format(self))
        time.sleep(0.01)

      log(DEBUG-1,'comedi: (%s) finished', self)
      # cancel the command to allow INSN_CONFIG calls (such as
      # get_cmd_timing_constraints) to complete--INSN_CONFIG are not allowed
      # when the subdevice is busy.
      self.stop()


  def stop(self):
    if self.busy:
      debug('comedi: cancelling cmd for %s', self)
      raiserr( comedi.cancel(self.card, self.subdevice), 'cancel' )


  def get_config_template(self):
    return self.config_template.copy()

  config_template = {
    'trigger' : {
      'enable' : {
        'value' : False,
        'type' : bool,
        'range' : None,
      },
      'source' : {
        'value' : '',
        'type' : str,
        'range' : None,
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
      'range' : None,
    },
    'clock-edge' : {
      'value' : 'rising',
      'type' : str,
      'range' : [
        ('falling','Sample on Falling Edge of Trigger'),
        ('rising', 'Sample on Rising Edge of Trigger'),
      ],
    },
  }




def create_chanlist(cr_pack, channels):
  """
  Add all channels to the chanlist array.
  """
  cmd_chanlist = ( ctypes.c_uint * len(channels) )()

  for i, (chname, chinfo) in izip( xrange( len(channels) ), channels ):
    cmd_chanlist[i] = cr_pack( chname, chinfo )
  return cmd_chanlist
