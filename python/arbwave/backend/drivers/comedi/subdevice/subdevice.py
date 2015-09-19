# vim: ts=2:sw=2:tw=80:nowrap

import copy, time, mmap, re
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
import numpy as np
import ctypes
from itertools import izip

from physical import unit

from .. import ctypes_comedi as clib

from .....tools.signal_graphs import nearest_terminal
from .....tools.cmp import cmpeps
from ....device import Device as Base
from .. import channels


command_test_errors = {
  0: 'invalid comedi command',
  1: 'unsupported trigger in ..._src setting of comedi command, setting zeroed',
  2: '..._src setting not supported by driver',
  3: 'TRIG argument of comedi command outside accepted range',
  4: 'adjusted TRIG argument in comedi command',
  5: 'chanlist not supported by board',
}



class Subdevice(Base):
  """
  In the context of Arbwave, a comedi subdevice is actually a represetation of
  what Arbwave considers to be a self-contained device.
  """

  #for continuous mode, this appears to be a magic value! fix the dumb kernel:
  # self.cmd.stop_arg = 1
  STOP_ARG_CONTINUOUS = 1
  subdev_type         = None  # changed by inheriting device types
  units               = clib.UNIT_volt
  default_range_min   = 0
  default_range_max   = 1

  def __init__(self, route_loader, card, subdevice, name_uses_subdev=False):
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
    self.clocks = None
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0
    self.cmd = clib.comedi_cmd()
    self.cmd_chanlist = None

    #first find the possible trigger and clock sources
    clk = self.name + '/SampleClock'
    trg = self.name + '/StartTrigger'

    if clk not in route_loader.dst_to_src:
        error("No clocks found for clock-able device '%s' (%s)",
              self, self.card.board)

    if trg not in route_loader.dst_to_src:
        warn ("No triggers found for triggerable(?) device '%s' (%s)",
              self, self.card.board)

    self.clock_sources = route_loader.dst_to_src.get(clk, list())
    self.trig_sources  = route_loader.dst_to_src.get(trg, list())

    self.config = self.get_config_template()


  def __del__(self):
    self.clear()

  def clear(self):
    debug( 'comedi: cancelling commands for comedi subdevice %s', self )
    clib.comedi_cancel( self.card, self.subdevice )
    self.t_max = 0.0
    ctypes.memset( ctypes.byref(self.cmd), 0, ctypes.sizeof(self.cmd) )
    del self.cmd_chanlist
    self.cmd_chanlist = None


  def get_config(self, L):
    """
    Simple accessor for configuration items.  This is primarily used so that
    subclasses can have differnt names, or even static values, for similar
    config concepts.
    """
    if type(L) not in [list, tuple]:
      return L

    C = self.config
    for li in L:
      C = C[li]
    return C


  @property
  def prefix(self):
    return self.card.prefix

  @property
  def flags(self):
    return clib.comedi_get_subdevice_flags(self.card, self.subdevice)

  @property
  def busy(self):
    return self.flags & clib.SDF_BUSY

  @property
  def running(self):
    return self.flags & clib.SDF_RUNNING

  @property
  def buf_size(self):
    return clib.comedi_get_buffer_size(self.card, self.subdevice)

  #@property
  def status(self):
    class Dict(dict):
      def __init__(self, *a, **kw):
        super(Dict,self).__init__(*a, **kw)
        self.__dict__ = self

    flags = self.flags
    D = Dict(
      busy                  =     bool(flags & clib.SDF_BUSY),
      busy_owner            =     bool(flags & clib.SDF_BUSY_OWNER),
      locked                =     bool(flags & clib.SDF_LOCKED),
      lock_owner            =     bool(flags & clib.SDF_LOCK_OWNER),
      maxdata_per_channel   =     bool(flags & clib.SDF_MAXDATA),
      flags_per_channel     =     bool(flags & clib.SDF_FLAGS),
      rangetype_per_channel =     bool(flags & clib.SDF_RANGETYPE),
      async_cmd_supported   =     bool(flags & clib.SDF_CMD),
      soft_calibrated       =     bool(flags & clib.SDF_SOFT_CALIBRATED),
      readable              =     bool(flags & clib.SDF_READABLE),
      writeable             =     bool(flags & clib.SDF_WRITEABLE),
      internal              =     bool(flags & clib.SDF_INTERNAL),
      aref_ground_supported =     bool(flags & clib.SDF_GROUND),
      aref_common_supported =     bool(flags & clib.SDF_COMMON),
      aref_diff_supported   =     bool(flags & clib.SDF_DIFF),
      aref_other_supported  =     bool(flags & clib.SDF_OTHER),
      dither_supported      =     bool(flags & clib.SDF_DITHER),
      deglitch_supported    =     bool(flags & clib.SDF_DEGLITCH),
      running               =     bool(flags & clib.SDF_RUNNING),
      sample_32bit          =     bool(flags & clib.SDF_LSAMPL),
      sample_16bit          = not bool(flags & clib.SDF_LSAMPL),
      sample_bitwise        =     bool(flags & clib.SDF_PACKED),
    )
    return D

  @property
  def available_channels(self):
    klass = channels.klasses[self.subdev_type]

    return [
      klass('{}{}'.format(self, i), self)
      for i in xrange(clib.comedi_get_n_channels( self.card, self.subdevice ))
    ]


  def config_all_channels(self):
    """
    Configure all channels and return them.

    Actually just calls self._config_all_channels(self.channels)
    """
    return self._config_all_channels(self.channels)


  def _config_all_channels(self, channels):
    """
    Configure all given channels and return them.
    """
    dflt_mn = self.get_config( default_range_min )
    dflt_mx = self.get_config( default_range_max )

    self.ranges = dict()
    self.maxdata = dict()
    C, S = self.card, self.subdevice
    for chname, chinfo in channels.items():
      mx = chinfo.get('max', dflt_mx)
      mn = chinfo.get('min', dflt_mn)
      ch = self.get_channel(chname)

      self.ranges[chname]=r=clib.comedi_find_range(C, S, ch, self.units, mn, mx)
      self.maxdata[chname] = clib.comedi_get_maxdata(C, S, ch)

      assert r >= 0, 'comedi: Could not identify output range for '+chname

      # if self.ranges[chname] >= 0:
      #   continue

      # simple find did not work, try harder (?)
      #ch_ranges = [
      #  ( i, clib.comedi_get_range(C, S, ch, i) )
      #  for i in xrange( comedi.comedi_get_n_ranges( C, S, ch ) )
      #]

      #ch_ranges.sort(key = lambda ri : ri[1].contents.max - ri[1].contents.min)
    return channels



  def cmd_is_continuous(self):
    """
    Tests the comedi_cmd to see if it was configured for continuous mode.
    """
    return self.cmd.stop_arg == self.STOP_ARG_CONTINUOUS


  def set_config(self, config=None, channels=None, shortest_paths=None):
    debug('comedi[%s].set_config', self)

    if channels and self.channels != channels:
      self.channels = channels
    if config and self.config != config:
      self.config = config

    if not self.config['clock']['value']:
      self.clock_terminal = None
    else:
      self.clock_terminal = \
          nearest_terminal( self.config['clock']['value'],
                              set(self.clock_sources),
                              shortest_paths )

    if self.clock_terminal == 'internal':
      # FIXME:  implement this mapping and value
      clock_args   = ( clib.TRIG_TIMER, internal_clock_value )
    else:
      #FIXME:  set this to correct mapped value
      channel = invert = 0
      if config['clock-edge']['value'] == 'falling':
        invert = clib.CR_INVERT
      #ian's claim:  if digital scan_begin_arg ==> cant have CR_EDGE
      clock_args = ( clib.TRIG_EXT, channel | clib.CR_EDGE | invert )

    trigger_args = ( clib.TRIG_INT, 0 )
    if self.config['trigger']['enable']['value']:
      #FIXME:  set this to correct mapped value
      channel = invert = 0
      if self.config['trigger']['edge']['value'] == 'falling':
        invert = clib.CR_INVERT
      trigger_args = ( clib.TRIG_EXT, channel | clib.CR_EDGE | invert )



    # NOW WE ARE READY TO ACTUAL CONFIGURE...
    # start with a clean slate:
    self.clear()

    debug( 'comedi: creating command:  %s', self.name )

    #### Now set self.cmd ####
    channels = self.config_all_channels().items()
    channels.sort( key = lambda i : i[1]['order'] )
    self.chanlist = create_chanlist(self.cr_pack, channels)

    self.cmd.subdev         = self.subdevice
    self.cmd.flags          = clib.TRIG_WRITE #bitwise or'd subdevice flags
    self.cmd.chanlist       = self.cmd_chanlist
    self.cmd.chanlist_len   = len( self.chanlist )
    self.cmd.start_src      = trigger_args[0]
    self.cmd.start_arg      = trigger_args[1]
    self.cmd.scan_begin_src = clock_args[0]
    self.cmd.scan_begin_arg = clock_args[1]
    self.cmd.convert_src    = clib.TRIG_NOW # accpets: TRIG_TIMER, TRIG_EXT, TRIG_NOW
    self.cmd.convert_arg    = 0
    self.cmd.scan_end_src   = clib.TRIG_COUNT
    self.cmd.scan_end_arg   = len( self.chanlist ) # iterate through all channels
    self.cmd.stop_src       = clib.TRIG_COUNT # accepts: TRIG_COUNT, TRIG_NONE
    self.cmd.stop_arg       = 0 # we'll set this at the time of set_waveforms
    #### finished init of self.cmd ####

    #### start testing cmd ####
    # FIXME:  should probably check to see if/how much the test is changing cmd
    for  i in xrange(2):
      # recommended number of times to call comedi_command_test is: 2
      test = clib.comedi_command_test(self.card, self.cmd)

      if test < 0:
        error ('invalid comedi command for %s', self)
      elif test > 0:
        warn( 'comedi[%s]: %s', self, command_test_errors[test] )
        continue


  def set_clocks(self, clocks):
    """
    Implemented by Timing channel
    """
    raise NotImplementedError('only the Timing task can implement clocks')


  def get_channel(self, name):
    return int( re.search('ao([0-9]*)$', name).group(1) )


  def convert_data(self, chname, data):
    """
    Takes data in physical units and converts it to lsampl_t data that comedi
    needs.
    """
    return clib.comedi_from_phys(data,self.ranges[chname],self.maxdata[chname])


  def cr_pack(self, chname, chinfo):
    """
    Packs data properly whether this is digital or analog
    """
    return clib.CR_PACK(
      self.get_channel(chname),
      self.ranges[chname],
      self.get_config(reference_value),
    )


  def set_output(self, data):
    """
    Sets a static value on each output channel of this task.
    """
    data = data.items()
    data.sort( key = lambda i : self.channels[i[0]]['order'] )

    insn_list = clib.comedi_insnlist()
    insn_list.set_length( len(data) )
    # we allocate the data to ensure it does not get garbage collected too soon
    L = [ clib.lsampl_t() for i in xrange( len(data) ) ]

    for i, (chname, value), di in izip( insn_list, data, L ):
      di.value = self.convert_data( chname, value )

      i.insn = clib.INSN_WRITE
      i.subdev = self.subdevice
      i.chanspec = self.cr_pack(chname, self.channels[chname])
      i.n = 1
      i.data = ctypes.pointer( di )
    clib.comedi_do_insnlist( self.card, insn_list )


  def get_min_period(self):
    #important function for Arbwave to use clocks
    #below is effective for timing subdevices
    #getting a period of a non-subdevice signal will need a dictionary with their period

    if self.subdev_type == 'to':
      chan = 0 #I think this is what we want
      clock = clib.lsampl_t()
      period = clib.lsampl_t()
      clib.comedi_get_clock_source(self.card, self.subdevice, chan, clock, period)
      print self.subdevice, "timing device"
      return int(period.value)*unit.ns
    else:
      return 0*unit.ns

  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.
    """
    assert not self.status.sample_bitwise, 'Please implement Bitwise cmd data'
    assert not self.status.sample_16bit, 'Please implement 16bit cmd data'

    if not self.clock_terminal:
      raise UserWarning('cannot start waveform without an output clock defined')

    my_clock = clock_transitions[ self.config['clock']['value'] ]
    dt_clk = my_clock['dt']
    transitions = list( my_clock['transitions'] )
    transitions.sort()

    # 3.  Data write
    # 3a.  Get data array
    # loop through each transition and accumulate a list of scans for each
    # channel for each transition.
    # probably need to do some rounding to the nearest clock pulse to ensure
    # that we only have pulses matched to the correct transition

    name = self.subdev_type


    chlist = ['{}/{}'.format(name, str(ch)) for ch in xrange(clib.comedi_get_n_channels(self.card, self.subdevice))]

    assert set(chlist).issuperset( waveforms.keys() ), \
      'NIDAQmx.set_output: mismatched channels'

    # get all the waveform data into the scans array.  All remaining None values
    # mean that the prior value for the particular channels(s) should be kept
    # for that scan.
    n_channels = len(waveforms)
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
    ##scans = [ scans[t]  for t in transitions ]


    # Set output to either continuous or one-time
    if continuous:
      self.cmd.stop_arg = self.STOP_ARG_CONTINUOUS
    else:
      # should be (number repetitions)*(buffer len)
      # for us, number repetitions == 1
      self.cmd.stop_arg = len(data)


    # 3b.  Send data to hardware

    self.start()

    print self.buf_size, "buf sz"
    mapp = mmap.mmap(clib.comedi_fileno(self.card), self.buf_size, mmap.MAP_SHARED, mmap.PROT_WRITE, 0, 0)

    npmap = np.ndarray(shape=((self.buf_size/2)), dtype=clib.sampl_t, buffer = mapp, offset=0, order='C')

    rng = self.channels[self.channels.keys()[0]] #this assumes all chans on subdevice have the same range

    rng = clib.comedi_range( rng['min'], rng['max'], 0 )

    print len(scans), 'len scans'
    for i in xrange((len(scans))):
      #TO DO: implement calibration
      ############################
      #num = re.search('([0-9]*)$', data.keys()[i])
      #chan = int(num.group())
      #poly = clib.comedi_polynomial_t()

      ##include findable rng integer PACK
      #rng = 0

      ##below is device dependenent, but can be discovered and selected using subdevice flag SDF_SOFT_CALIBRATED

      #path = clib.comedi_get_default_calibration_path(self.card)

      #path_point = comedi_
      #calibration = clib.comedi_parse_calibration_file(path)
      ##print calibration[0]
      #clib.comedi_get_softcal_converter(self.subdevice,chan,rng, clib.COMEDI_FROM_PHYSICAL,calibration, poly)

      #npmap[i] = clib.comedi_from_physical(data[data.keys()[i]], poly)
      ############################

      npmap[scans.keys()[i]:(self.buf_size/2)] = clib.comedi_from_phys(scans[scans.keys()[i]][0], rng, clib.lsampl_t(65535)) #max data will be device specific?
      #need to account for multiple chans in 'scans'

    print 'cmd: ', self.cmd
    print len (mapp), len (npmap)
    print clib.comedi_mark_buffer_written(self.card, self.subdevice, self.buf_size), "write"
    print clib.comedi_internal_trigger(self.card, self.subdevice, 0), "trig"

    while(0): #protects from buffer underwrite
      print clib.comedi_get_buffer_contents(self.card, self.subdevice)

      unmarked = self.buf_size - clib.comedi_get_buffer_contents(self.card, self.subdevice)
      #print unmarked, 'A'
      #if unmarked > 0:
      #  clib.comedi_mark_buffer_written(self.card, self.subdevice, unmarked)
      #  print unmarked, 'B'
    #while loop should be unnecessary with TRIG_COUNT and stop_arg = 1

    self.t_max = t_max


  def start(self):
    if not self.busy:
      clib.comedi_command(self.card, self.cmd)


  def wait(self):
    if self.running:
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


  def stop(self):
    if self.running:
      clib.comedi_cancel(self.card, self.subdevice)
      # # this seems a little drastic, but I think Ian found this necessary
      # clib.comedi_close(self.card) #put in card.py?



  def get_config_template(self):
    return {
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
