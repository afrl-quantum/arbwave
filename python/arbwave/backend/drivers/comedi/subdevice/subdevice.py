# vim: ts=2:sw=2:tw=80:nowrap

import copy, time, mmap, re
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
import numpy as np

from physical import unit

from .. import ctypes_comedi as clib

from .....tools.signal_graphs import nearest_terminal
from .....tools.cmp import cmpeps
from ....device import Device as Base
from .. import channels

class Subdevice(Base):
  """
  In the context of Arbwave, a comedi subdevice is actually a represetation of
  what Arbwave considers to be a self-contained device.
  """

  STATIC              = 0
  WAVEFORM_SINGLE     = 1
  WAVEFORM_CONTINUOUS = 2
  subdev_type         = None  # changed by inheriting device types
  
  def __init__(self, route_loader, card, subdevice, name_uses_subdev=False):
    if name_uses_subdev: devname = '{}{}'.format(self.subdev_type, subdevice)
    else:                devname = self.subdev_type
    name = '{}/{}'.format(card, devname)
    Base.__init__(self, name=name)
    self.base_name = devname
    self.card = card
    self.subdevice = subdevice
    debug( 'loading comedi subdevice %s', self )
    self.task = True #TO DO: get rid of this
    self.channels = dict()
    self.clocks = None
    self.clock_terminal = None
    self.use_case = None
    self.t_max = 0.0
    self.chan_index_list = list()
    self.cmd = clib.comedi_cmd()
    self.sources_to_native = dict() # not sure if we need this
    
    
      
    # below should be re done in a device agnostic way. 
    if not self.subdev_type == 'to': #should take care of this in timing.py
      
      #first find the possible trigger and clock sources
      #this method is ni dependent! might be woth a total reworking in light of routing in card.py
      clk = self.name + '/SampleClock'
      #trg = self.name + '/StartTrigger'
      trg = "comedi/Dev0/ao/StartTrigger" #Spencer removed di/do start trigger from ni routes for some reason so I have to cheat here for testing
      
    else: 
      
      index = str(self.subdevice - clib.comedi_find_subdevice_by_type(self.card,clib.COMEDI_SUBD_COUNTER,0))
      
      clk = str(self.card) + '/Ctr'+index+'Source' 

      trg = str(self.card) +'/Ctr'+index+'Gate' # wrong, timing devices have different commands and shouldnt need triggers like this
      
      devname = 'Ctr'+index          # bad place for this
      name = '{}/{}'.format(self.card, devname)
      Base.__init__(self, name=name)
      self.base_name = devname      


    if clk not in route_loader.source_map:
        error("No clocks found for clock-able device '%s' (%s)",
              self, self.card.board)

    if trg not in route_loader.aggregate_map:
        error("No triggers found for triggerable device '%s' (%s)",
              self, self.card.board)
    
    self.clock_sources = route_loader.source_map[clk]
    self.trig_sources  = route_loader.aggregate_map[trg] #changed to agg map because it contains starttrigger for do, may be incorrect
      
      
    self.config = self.get_config_template()


  def __del__(self):
    self.clear()


  def clear(self):
      
      debug( 'comedi: cancelling commands for comedi subdevice %s', self )
      clib.comedi_cancel( self.card, self.subdevice )
      self.t_max = 0.0

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
    flags = self.flags
    D = dict(
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
    #D.__dict__ = D
    return D

  @property
  def available_channels(self):
    klass = channels.klasses[self.subdev_type]
    
    return [
      klass('{}/{}'.format(self, i), self)
      for i in xrange(clib.comedi_get_n_channels( self.card, self.subdevice ))
    ]

  def add_channels(self):
    """
    Sub-task types must override this for specific channel creation.
    """


  def dump_cmd(self, cmd):
    print "---------------------------"
    print "command structure contains:"
    print "cmd.subdev : ", cmd.subdev
    print "cmd.flags : ", cmd.flags
    print "cmd.start :\t", cmd.start_src, "\t", cmd.start_arg
    print "cmd.scan_beg :\t", cmd.scan_begin_src, "\t", cmd.scan_begin_arg
    print "cmd.convert :\t", cmd.convert_src, "\t", cmd.convert_arg
    print "cmd.scan_end :\t", cmd.scan_end_src, "\t", cmd.scan_end_arg
    print "cmd.stop :\t", cmd.stop_src, "\t", cmd.stop_arg
    print "cmd.chanlist : ", cmd.chanlist
    print "cmd.chanlist_len : ", cmd.chanlist_len
    print "cmd.data : ", cmd.data
    print "cmd.data_len : ", cmd.data_len
    print "---------------------------"

  
  
  def cmd_config(self, config):
    """
    Takes values from config and configures a comedi command
    """

    if not config['trigger']['enable']['value']:
      start_src = clib.TRIG_INT
      start_arg = 0
    else:
      start_src = clib.TRIG_EXT
      if config['trigger']['edge']['value'] == 'rising':
        start_arg = clib.CR_EDGE
      if config['trigger']['edge']['value'] == 'falling':
        start_arg = clib.CR_INVERT | clib.CR_EDGE
    
    
    if config['clock-settings']['mode']['value'] == 'finite':
      stop_src = clib.TRIG_COUNT
      #stop_arg actually should take the ammount of buffer to run through
      #stop_arg = 1 may allow for continuous genertion
      stop_arg = 1 #should be: (desired count)*(buffer len)

    else:
      stop_src = clib.TRIG_COUNT
      stop_arg = 1
      
    if config['clock-settings']['edge']['value'] == 'rising':
        scan_begin_arg = clib.CR_EDGE
    if config['clock-settings']['edge']['value'] == 'falling':
        scan_begin_arg = clib.CR_INVERT | clib.CR_EDGE
    
    #Below calls Card class method to provide integers understood by comedi cmds
    trig_signal = {(config['trigger']['source']['value'], self.name+'/StartTrigger'): {'invert': False}}
    trig = self.card.Sigconfig(trig_signal)
    
    
    clk_signal = {(self.clock_terminal, self.name+'/SampleClock'): {'invert': False}}
    clk = self.card.Sigconfig(clk_signal)
    
    if trig == None:
      start_src = clib.TRIG_INT
      start_arg, trig = 0, 0
    
    if clk == None:
      scan_begin_src = clib.TRIG_TIMER
      scan_begin_arg = 0
      clk = 1200 #int((1e9/100000))
    else:
      scan_begin_src = clib.TRIG_EXT
      scan_begin_arg = clib.CR_EDGE
      #if digital scan_begin_arg ==> cant have CR_EDGE
   
    self.add_channels() # populates cmd_chanlist
    
     #TRIG_EXT argument: digital line of trigger (watch for inconisitent PFI index)
     #TRIG_INT argument: Zero, triggers with: comedi_internal_trigger(card, subdevice, 0)
     #TRIG_COUNT argument: int counted to
     #all other arguments are zero
                 
    self.cmd.subdev = self.subdevice 
    self.cmd.flags = clib.TRIG_WRITE #bitwise or'd subdevice flags
    self.cmd.start_src = start_src # start trigger source accepts: TRIG_INT, TRIG_EXT
    self.cmd.start_arg = start_arg | trig
    self.cmd.scan_begin_src = scan_begin_src # accepts: TRIG_TIMER, TRIG_EXT
    self.cmd.scan_begin_arg = scan_begin_arg | clk
    self.cmd.convert_src = clib.TRIG_NOW # accpets: TRIG_TIMER, TRIG_EXT, TRIG_NOW
    self.cmd.convert_arg = 0
    self.cmd.scan_end_src = clib.TRIG_COUNT
    self.cmd.scan_end_arg = len ( self.cmd_chanlist[:] )
    self.cmd.stop_src = stop_src # accepts: TRIG_COUNT, TRIG_NONE
    self.cmd.stop_arg = stop_arg #for some reason TRIG_COUNT with stop_arg = 1 gives continuous waveform
    self.cmd.chanlist = self.cmd_chanlist #pointer to array with elements --> clib.CR_PACK(chan, range, aref) 
    self.cmd.chanlist_len = len ( self.cmd_chanlist[:] ) # wrong way to do this?
    
    #self.dump_cmd(self.cmd)
    
    for  i in xrange(2):
    
      test = clib.comedi_command_test(self.card, self.cmd)

      if test < 0:
          error ('invalid comedi command for %s', self)
      if test == 1:
          warn ('unsupported trigger in ..._src setting of comedi command, setting zeroed')
      if test == 2:
          warn ('..._src setting not supported by driver')
      if test == 3:
          warn ('TRIG argument of comedi command outside accepted range')
      if test == 4:
          warn ('adjusted TRIG argument in comedi command')
      if test == 5:
          warn ('chanlist not supported by board')
      if test == 0:
          print "command configuration"
          continue

  
  def set_config(self, config=None, channels=None, shortest_paths=None,
                 force=False):
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
      self.clock_terminal = \
          nearest_terminal( self.config['clock']['value'],
                              set(self.clock_sources),
                              shortest_paths ) 
      
      force = True
    
    if force:
      self._rebuild_cmd()
    
    
  def _rebuild_cmd(self):
    # rebuild the command
    self.clear()
    
    if not self.channels:
      return
    debug( 'comedi: creating command:  %s', self.name )
    
    self.cmd_chanlist = (clib.lsampl_t*len(self.channels))()
    
    self.cmd_config(self.config)
    
    self.use_case = None


  def set_clocks(self, clocks):
    """
    Implemented by Timing channel
    """
    raise NotImplementedError('only the Timing task can implement clocks')


  def set_output(self, data):
    """
    Sets a static value on each output channel of this task.
    """
    
    if self.channels:
      
      if self.use_case in [ None, self.STATIC ]:
        if self.use_case is not None:
          debug( 'comedi: stopping task: %s', self.name)
          self.stop()
      else: 
      
        self._rebuild_cmd()

        self.use_case = self.STATIC

      if self.subdev_type == 'do':  #had to include this here, because self.card wont work in digital.py
        
        bits = 0
        
        for i in self.chan_index_list:
          clib.comedi_dio_config(self.card, self.subdevice, i, clib.COMEDI_OUTPUT)
          print "dio_config_output", i
          if data['do'+str(i)] == True:
            bits = bits|(2**i)
            
        bits = (clib.lsampl_t*1)(bits)
      
        clib.comedi_dio_bitfield2(self.card,2, clib.lsampl_t((2**(max(self.chan_index_list)+1))-1), bits, 0)
     
      else:
        
        #Because static output is not timing sensitive, this should be done
        #using premade comedi function clib.comedi-data_write
        #optional: implement calibration
        
        self.start() 

        mapp = mmap.mmap(clib.comedi_fileno(self.card), self.buf_size, mmap.MAP_SHARED, mmap.PROT_WRITE, 0, 0) #
        npmap = np.ndarray(shape=((self.buf_size/2)), dtype=clib.sampl_t, buffer = mapp, offset=0, order='C')


        for i in xrange((len(data))):
          rng = self.channels[self.channels.keys()[i]]
          rng = clib.comedi_range( rng['min'], rng['max'], 0 )
          npmap[:] = clib.comedi_from_phys(data[data.keys()[i]], rng, clib.lsampl_t(65535)) #max data will be device specific?

        print clib.comedi_mark_buffer_written(self.card, self.subdevice, self.buf_size), "written"
        print clib.comedi_internal_trigger(self.card, self.subdevice, 0), "trigger"
        
        
        

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
    
    if self.channels:
      if self.use_case in [ None, self.STATIC, self.WAVEFORM_SINGLE, self.WAVEFORM_CONTINUOUS ]:
        if self.use_case is not None:
          debug( 'comedi: stopping task: %s', self.name)
          self.stop()
      else: 
        self._rebuild_cmd()
        
      if continuous:
        self.use_case = self.WAVEFORM_CONTINUOUS
        continuous == True
      else:
        self.use_case = self.WAVEFORM_SINGLE
        continuous == False
    
    if not self.clock_terminal:
      raise UserWarning('cannot start waveform without a output clock defined')

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
        zero_if_none(v,i) for v,i in zip( S0, xrange(len(S0)) )
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
       
    self.dump_cmd(self.cmd)  
    
    print len (mapp), len (npmap)
    
    print clib.comedi_mark_buffer_written(self.card, self.subdevice, self.buf_size), "write"
      
    print clib.comedi_internal_trigger(self.card, self.subdevice, 0), "trig"
    
    
       
    while(0): #protects from buffer underwrite
         print clib.comedi_get_buffer_contents(self.card, self.subdevice)
         
         unmarked = self.buf_size - clib.comedi_get_buffer_contents(self.card, self.subdevice)
         #print unmarked, 'A'
         #if unmarked > 0:
          
         #   clib.comedi_mark_buffer_written(self.card, self.subdevice, unmarked)
            #print unmarked, 'B'
    #while loop should be unnecessary with TRIG_COUNT and stop_arg = 1
    
    
    self.t_max = t_max
    

  def start(self):
    if self.task:
      clib.comedi_command(self.card, self.cmd)


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
      clib.comedi_cancel(self.card, self.subdevice)
      # this seems a little drastic, but I think Ian found this necessary
      clib.comedi_close(self.card) #put in card.py?



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
