#!/usr/bin/env python




# This file is a stand-alone comedi command for testing various concepts. Currently it should generate 
# continuous sine wave.



import ctypes_comedi as comedi
from ctypes_comedi import *
import numpy as np
from ctypes import byref, pointer
import mmap
from mmap import PROT_WRITE, MAP_SHARED
import sys





def dump_cmd(cmd):
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


class Test(object):
  def __init__(self, do_generic=False, subdev = 1, freq = 500000):
    self.do_generic = do_generic
    self.freq = freq
    self.subdev = subdev
    self.open()

  def open(self):
    self.d0 = comedi.comedi_open('/dev/comedi0')   
    
    self.size = comedi_get_buffer_size(self.d0, self.subdev)
    self.num_samples = self.size/2 
    
    self.map = mmap.mmap(comedi_fileno(self.d0), self.size, MAP_SHARED, PROT_WRITE, 0, 0)
    self.npmap = np.ndarray(shape=self.num_samples, dtype=sampl_t, buffer=self.map, offset=0, order='C')

  def stop(self):
    comedi.comedi_cancel(self.d0,self.subdev)

  def close(self):
    del self.npmap
    self.map.close()
    del self.map
    comedi_dio_config(d0, 7, 2, COMEDI_INPUT)
    comedi_dio_config(d0, 2, 0, COMEDI_INPUT)
    comedi_dio_config(d0, 2, 1, COMEDI_INPUT)
    comedi_dio_config(d0, 2, 2, COMEDI_INPUT)
    
    comedi.comedi_close(self.d0)
    del self.d0
    
  def __del__(self):
    self.close()
    
  def __call__(self):
    cmd = comedi_cmd_struct()
    #dump_cmd(cmd)
    nchans = 1



    chanlist = (comedi.lsampl_t*nchans)()

    for i in range(nchans):
      chanlist[i] = 0

    if self.do_generic:
      comedi_get_cmd_generic_timed(self.d0, self.subdev, cmd, nchans, int(10e9))

    #dump_cmd(cmd)
    
    comedi_dio_config(self.d0, 7, 5, COMEDI_INPUT)
    #print comedi_set_routing(self.d0, 7, 5, 0)
    
    #comedi_dio_config(self.d0, 7, 1, COMEDI_OUTPUT)
    #comedi_set_routing(self.d0,7, 1, NI_PFI_OUTPUT_RTSI0 + 1)
    
    cmd.subdev = self.subdev
    cmd.flags = 0
    cmd.start_src = TRIG_INT
    cmd.start_arg = 0
    cmd.scan_begin_src = TRIG_TIMER #TRIG_TIMER
    cmd.scan_begin_arg =  0 #
    cmd.convert_src = TRIG_NOW
    cmd.convert_arg = 0
    cmd.scan_end_src = TRIG_COUNT
    cmd.scan_end_arg = 1                                                                             
    cmd.stop_src = TRIG_COUNT
    cmd.stop_arg = 1     

    cmd.chanlist = chanlist
    cmd.chanlist_len = nchans

    

    #dump_cmd(cmd)

    print comedi_command_test(self.d0, cmd), "test"  #for some reason test changes flag from TRIG_ROUND_NEAREST to TRIG_WRITE

    dump_cmd(cmd)

    #print comedi_command_test(self.d0, cmd), "test"
    print comedi_command(self.d0, cmd), "cmd" 

    amplitude = 65535
    offset = 65535/2    
    self.write_waveform(self.num_samples, amplitude, offset)
    print comedi_mark_buffer_written(self.d0, self.subdev, self.size), "buffer" 
    
    bits = (lsampl_t*1)(63)
    
    comedi_dio_bitfield2(self.d0,2, lsampl_t(63), bits, 0)
    
    print comedi_internal_trigger(self.d0, self.subdev, 0), "trig"

    while(1):
      
      unmarked = self.size - comedi_get_buffer_contents(self.d0, self.subdev)
      
      if unmarked > 0:
      
        comedi_mark_buffer_written(self.d0, self.subdev, unmarked)


  def write_waveform(self, size, amplitude, offset):
      x = np.r_[0:self.num_samples]
      self.npmap[:] = (amplitude/2)*np.sin((2*np.pi*x)/ (.5*self.num_samples)) + offset

        
  



if __name__ == '__main__':
  print 2
  test = Test()
  test()
  raw_input('Press enter to quit')
