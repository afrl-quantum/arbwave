# vim: ts=2:sw=2:tw=80:nowrap

import re, glob, traceback
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog
from ....tools.path import collect_prefix
from ...driver import Driver as Base
from device import Device
import re
import ctypes_comedi as c


class Driver(Base):
  prefix = 'comedi'
  description = 'Comedi Driver'
  has_simulated_mode = False # will not be a lie some time in the future

  @staticmethod
  def glob_comedi_devices():
    """creates a list of all comedi devices"""
    return glob.glob('/dev/comedi*')


  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)
    # hook the simulated library if needed
    if self.simulated:
      import sim # rehook comedi lib so that hardware is simulated.
      Csim = sim.inject_sim_lib()
      self.glob_comedi_devices = Csim.glob_devices


    # device path --> Device instance
    self.devices     = dict()
    self.subdevices  = dict()
    self.analogs     = list()
    self.lines       = list()
    self.counters    = list()
    self.signals     = list()
    self.routed_signals = dict()
    
    for df in self.glob_comedi_devices():
      if Device.parse_dev( df ) is None:
        continue # don't match subdevices
      try:
        d = Device( self, df )
      except:
        traceback.print_exc()
        print 'Could not open comedi device: ', df
        continue
      self.devices[ str(d) ] = d
      self.subdevices.update( d.subdevices )
      self.analogs  += [ ao for sub in d.ao_subdevices for ao in sub.available_channels ]
      self.lines    += [ do for sub in d.do_subdevices for do in sub.available_channels ]
      self.lines    += [ do for sub in d.dio_subdevices for do in sub.available_channels ]
      self.counters += [ co for sub in d.counter_subdevices for co in sub.available_channels ]
      self.signals  += [ so for  so in d.signals ]
      for i in xrange(len(sub.available_channels)):
        
        print sub.available_channels[i]
    print 'found {} comedi supported boards'.format(len(self.devices))


  def close(self):
    """
    Close each device.  Each device will first close each of its subdevices.
    """
    while self.devices:
      devname, dev = self.devices.popitem()
      debug( 'closing comedi device: %s', devname )
      del dev

  def get_devices(self):
    """
    Actually, to fit into the framework here for Arbwave, we return the subdevices
    """
    return self.subdevices.values()

  def get_analog_channels(self):
    return self.analogs

  def get_digital_channels(self):
    return self.lines

  def get_timing_channels(self):
    return self.counters

  def get_routeable_backplane_signals(self):
    return self.signals


  def set_device_config( self, config, channels, shortest_paths ):
    
    debug('comedi.set_device_config')
    
    
    subdev_chans = dict()
    chans = dict()
    
    for s in self.subdevices.keys():
    
      subdev_pre = re.search('(\w*/\w*/\D*)', s)
      for c in channels:
        
        chan_pre = re.search('(\w*/\w*/\w*)', c) #could be more specific
          
        print subdev_pre.group(),chan_pre.group() 
        if subdev_pre.group() == chan_pre.group():
          
          subdev_chans.update( {c:channels[c]} )
       
      chans.update( {s:subdev_chans} )

    for d, sdev in self.subdevices.items():
      if d in config or d in chans:
        
        sdev.set_config( config.get(d,{}), chans.get(d,[]), shortest_paths )
    

  def set_clocks( self, clocks ):
    debug('comedi.set_clocks')
    clocks = collect_prefix(clocks, 0, 2, 2)
    for d, sdev in self.subdevices.items():
      if d in clocks:
        sdev.set_clocks( clocks[d] )


  def set_signals( self, signals ):
    debug('comedi.set_signals')
    
    signals = collect_prefix( signals, 0, 2, prefix_list=self.devices )
    
    #TO DO: this function doesnt exist yet
    ##for d, dev in self.devices.items():
    ##  dev.set_signals( signals.get(d,{}) )


  def set_static( self, analog, digital ):
    
    debug('comedi.set_static')
    D = collect_prefix(digital, 0, 2, 2)
    A = collect_prefix(analog, 0, 2, 2)
  
    #selects all valid subdevices insead of arbitrary choice
    #later we may want to select from available subdevices 
    for dev, data in D.items(): 
      for i in self.subdevices.keys():
        sdev = re.search(dev+"(/do[0-9]*)", i)
        if sdev:
          self.subdevices[ sdev.group() ].set_output( data ) 
          
    for dev, data in A.items():
      for i in self.subdevices.keys():
        sdev = re.search(dev+"(/ao[0-9]*)", i)
        if sdev:
          self.subdevices[ sdev.group() ].set_output( data ) 

  def set_waveforms( self, analog, digital, transitions,
                     t_max, end_clocks, continuous ):
    debug('comedi.set_waveforms')
    D = collect_prefix( digital, 0, 2, 2 )
    A = collect_prefix( analog, 0, 2, 2 )
    C = collect_prefix( transitions, 0, 2, 2)
    E = collect_prefix( dict.fromkeys( end_clocks ), 0, 2, 2)

    for d,sdev in self.subdevices.items():
      if d in D or d in C:
        sdev.set_waveforms( D.get(d,{}), C.get(d,{}), t_max, E.get(d,{}),
                            continuous )
    #for dev in A.items():
      #self.subdevices[ dev[0]+'/ao1' ] \
        #set_waveforms( dev[1], transitions, t_max, continuous )
