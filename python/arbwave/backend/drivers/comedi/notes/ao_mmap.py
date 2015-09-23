#!/usr/bin/env python

"""
Asynchronous Analog Output Example
Part of Comedilib

Copyright (c) 1999,2000 David A. Schleef <ds@schleef.org>

This file may be freely modified, distributed, and combined with
other software, as long as proper attribution is given in the
source code.



Requirements: Analog output device capable of
   asynchronous commands.

This demo uses an analog output subdevice with an
asynchronous command to generate a waveform.  The
demo hijacks for -n option to select a waveform from
a predefined list.  The default waveform is a sine
wave (surprise!).  Other waveforms include sawtooth,
square, triangle and cycloid.

The function generation algorithm is the same as
what is typically used in digital function generators.
A 32-bit accumulator is incremented by a phase factor,
which is the amount (in radians) that the generator
advances each time step.  The accumulator is then
shifted right by 20 bits, to get a 12 bit offset into
a lookup table.  The value in the lookup table at
that offset is then put into a buffer for output to
the DAC.

[ Actually, the accumulator is only 26 bits, for some
reason.  I'll fix this sometime. ]
"""

import os, sys, time
from os import path
sys.path.append( path.join( path.dirname(__file__), path.pardir ) )

import ctypes_comedi as clib
import numpy as np
from ctypes import byref, pointer, c_uint, sizeof
from mmap import mmap, PROT_WRITE, MAP_SHARED
from itertools import izip

import argparse


arefs = dict(
  common = clib.AREF_COMMON,
  ground = clib.AREF_GROUND,
)


class Test(object):
  #/* frequency of the sine wave to output */
  waveform_frequency  = 10.0

  #/* peak-to-peak amplitude, in DAC units (i.e., 0-4095) */
  amplitude    = 4000

  #/* offset, in DAC units */
  offset      = 2048

  #/* This is the size of chunks we deal with when creating and
  #   outputting data.  This *could* be 1, but that would be
  #   inefficient */
  ##define BUF_LEN 0x8000
  BUF_LEN = 0 # default to zero length
  size = 0

  def __init__(self, options):
    self.data = None
    self.cmd = clib.comedi_cmd()
    self.chanlist = ( c_uint * 16 )()

    #/* Use extra to select waveform */
    fn = options.waveform
    if fn < 0 or fn >= len( dds_list ):
      print "Use the option '-n' to select another waveform."
      fn = 0;

    if options.value:
      self.waveform_frequency = options.value

    dev = clib.comedi_open(options.filename)
    if not dev:
      print "error opening ", options.filename
      return -1;


    if options.subdevice < 0:
      options.subdevice = clib.comedi_find_subdevice_by_type(dev, clib.COMEDI_SUBD_AO, 0)


    self.subdevice_flags = clib.comedi_get_subdevice_flags(dev, options.subdevice)
    self.sampl_t = clib.sampl_t
    if self.subdevice_flags & clib.SDF_LSAMPL:
      self.sampl_t = clib.lsampl_t

    maxdata = clib.comedi_get_maxdata(dev, options.subdevice, options.channel)
    rng = clib.comedi_get_range(dev, options.subdevice, options.channel, options.range)

    self.offset = float( clib.comedi_from_phys(0.0, rng, maxdata) )
    self.amplitude = float( clib.comedi_from_phys(1.0, rng, maxdata) ) - self.offset

    #memset(&self.cmd,0,sizeof(self.cmd));
    self.cmd.subdev = options.subdevice
    self.cmd.flags = clib.CMDF_WRITE
    self.cmd.start_src = clib.TRIG_INT
    self.cmd.start_arg = 0
    self.cmd.scan_begin_src = clib.TRIG_TIMER
    self.cmd.scan_begin_arg = int( 1e9 / options.freq )
    self.cmd.convert_src = clib.TRIG_NOW
    self.cmd.convert_arg = 0
    self.cmd.scan_end_src = clib.TRIG_COUNT
    self.cmd.scan_end_arg = options.n_chan
    self.cmd.stop_src = clib.TRIG_NONE
    self.cmd.stop_arg = 0

    self.cmd.chanlist = self.chanlist
    self.cmd.chanlist_len = options.n_chan

    aref = arefs[ options.aref ]
    self.chanlist[0] = clib.CR_PACK(options.channel, options.range, aref)
    self.chanlist[1] = clib.CR_PACK(options.channel + 1, options.range, aref)
  
    dds = dds_list[options.waveform]( self.amplitude, self.offset,
                                      self.waveform_frequency, options.freq )

    if options.verbose:
      print 'cmd: ', self.cmd

    err = clib.comedi_command_test(dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command_test")
      return 1

    err = clib.comedi_command_test(dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command_test")
      return 1

    err = clib.comedi_command(dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command");
      return 1

    size = clib.comedi_get_buffer_size( dev, options.subdevice )
    print "buffer size is:", size
    self.BUF_LEN = size / sizeof(self.sampl_t)

    # The c version; we can cast directly
    #data = mmap(NULL, size, PROT_WRITE, MAP_SHARED, comedi_fileno(dev), 0)

    # the python version;  we must cast using ctypes
    mapped = mmap(clib.comedi_fileno(dev), size, prot=PROT_WRITE, flags=MAP_SHARED, offset=0)
    data = (self.sampl_t * self.BUF_LEN).from_buffer( mapped )
    if not data:
      #perror("mmap");
      print 'mmap: error!'
      return 1

    dds(data,self.BUF_LEN)
    n = self.BUF_LEN * sizeof(self.sampl_t)
    m = clib.comedi_mark_buffer_written(dev, options.subdevice, size)
    print "Marked {} out of {}".format(m, n)
    if m < 0:
      clib.comedi_perror("comedi_mark_buffer_written")
      return 1
    elif m < n:
      print "failed to preload output buffer with", n, "bytes, is it too small?"
      print "See the --write-buffer option of comedi_config"
      return 1

    if options.verbose:
      print "m=",m

    ret = clib.comedi_internal_trigger(dev, options.subdevice, 0)
    if ret < 0:
      print "comedi_internal_trigger:"
      os.strerror(ret)
      return 1

    time.sleep(100)
    # total = 0
    #//while(1){
    #//  dds(data,self.BUF_LEN);
    #//  n=self.BUF_LEN*sizeof(self.sampl_t);
    #//  while(n>0){
    #//    m=write(comedi_fileno(dev),(void *)data+(self.BUF_LEN*sizeof(self.sampl_t)-n),n);
    #//    printf("wrote..\n");
    #//    if(m<0){
    #//      perror("write");
    #//      exit(0);
    #//    }
    #//    if (options.verbose)
    #//      printf("m=%d\n",m);
    #//    n-=m;
    #//  }
    #//  total+=self.BUF_LEN;
    #//  //printf("%d\n",total);
    #//}

    return 0




class DDS(object):
  WAVEFORM_SHIFT  = 16
  WAVEFORM_LEN    = (1<<WAVEFORM_SHIFT)
  WAVEFORM_MASK   = (WAVEFORM_LEN-1)
  name            = None


  def __init__(self, amplitude, offset, waveform_frequency, update_frequency):
    self.amplitude = amplitude
    self.offset = offset
    self.adder = int( waveform_frequency / update_frequency
                      * (1 << 16) * (1 << self.WAVEFORM_SHIFT) )
    self.acc = 0;
    self.waveform = [0] * self.WAVEFORM_LEN
    self.init()

  def __call__(self, buf, n):
    for i in xrange( n ):
      buf[i] = int( self.waveform[(self.acc >> 16) & self.WAVEFORM_MASK] )
      self.acc += self.adder;

  def __str__(self):
    return self.name


class DDS_sine(DDS):
  name = 'sine'
  def init(self):
    ofs = self.offset
    amp = 0.5 * self.amplitude

    if(ofs < amp):
      # Probably a unipolar range.  Bump up the offset.
      ofs = amp
    for i in xrange(self.WAVEFORM_LEN):
      self.waveform[i]=round(ofs+amp*np.cos(i*2*M_PI/WAVEFORM_LEN))


def triangle(x):
  """Defined for x in [0,1]"""
  return (1.0 - x) if (x > 0.5) else x


class DDS_pseudocycloid(DDS):
  """
  Yes, I know this is not the proper equation for a cycloid.  Fix it.
  """
  name = 'pseudocycloid'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN/2 ):
      t=2*float(i)/self.WAVEFORM_LEN
      self.waveform[i]=round(self.offset+self.amplitude*np.sqrt(1-4*t*t))
    for i in xrange( self.WAVEFORM_LEN/2, self.WAVEFORM_LEN ):
      t=2*(1-float(i)/WAVEFORM_LEN)
      self.waveform[i]=round(self.offset+self.amplitude*np.sqrt(1-t*t))

class DDS_cycloid(DDS):
  name = 'cycloid'
  def init(self):
    SUBSCALE = 2 # Needs to be >= 2.

    i = -1;
    for h in xrange( self.WAVEFORM_LEN* SUBSCALE ):
      t = (h * (2 * np.pi)) / (self.WAVEFORM_LEN * SUBSCALE)
      x = t - np.sin(t)
      ni = int((x * self.WAVEFORM_LEN) / (2 * np.pi))
      if ni > i:
        i = ni
        y = 1 - np.cos(t)
        self.waveform[i] = round(self.offset + (self.amplitude * y / 2))

class DDS_ramp_up(DDS):
  name = 'ramp_up'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN ):
      self.waveform[i]=round(self.offset+self.amplitude*float(i)/self.WAVEFORM_LEN)

class DDS_ramp_down(DDS):
  name = 'ramp_down'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN ):
      self.waveform[i]=round(self.offset+self.amplitude*float(self.WAVEFORM_LEN-1-i)/self.WAVEFORM_LEN)

class DDS_triangle(DDS):
  name = 'triangle'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN ):
      self.waveform[i] = round(self.offset + self.amplitude * 2 * triangle(float(i) / self.WAVEFORM_LEN))

class DDS_square(DDS):
  name = 'square'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN/2 ):
      self.waveform[i] = round(self.offset)
    for i in xrange( self.WAVEFORM_LEN/2, self.WAVEFORM_LEN ):
      self.waveform[i] = round(self.offset + self.amplitude)

class DDS_blancmange(DDS):
  name = 'blancmange'
  def init(self):
    for i in xrange( self.WAVEFORM_LEN ):
      b = 0;
      for n in xrange( 16 ):
        x = float(i) / self.WAVEFORM_LEN
        x *= (1 << n)
        x -= int(x)
        b += triangle(x) / (1 << n)
      self.waveform[i] = round(self.offset + self.amplitude * 1.5 * b)





dds_list = [
  DDS_sine,
  DDS_ramp_up,
  DDS_ramp_down,
  DDS_triangle,
  DDS_square,
  DDS_cycloid,
  DDS_blancmange,
]


def process_args():
  parser = argparse.ArgumentParser()
  parser.add_argument( '-f', '--filename', nargs='?', default='/dev/comedi0',
    help='Comedi device file' )
  parser.add_argument( '-s', '--subdevice', type=int, default=-1 )
  parser.add_argument( '-n', '--n_chan', type=int, default=1 )
  parser.add_argument( '-c', '--channel', type=int, default=0 )
  parser.add_argument( '-a', '--aref',  choices=['ground', 'common'], default='ground' )
  parser.add_argument( '-r', '--range', type=int, default=0 )
  parser.add_argument( '-F', '--freq', type=float, default=1000. )
  parser.add_argument( '-v', '--value', nargs='?', type=float, default=0. )
  parser.add_argument( '-w', '--waveform', type=int, default=-1,
    help='\n\t'.join([ '{}: {}'.format(i,c.name)
           for i,c in zip(xrange(len(dds_list)), dds_list)]) )
  parser.add_argument( '-p', '--verbose', action='store_true' )
  return parser.parse_args()

def main(args):
  Test( process_args() )

if __name__ == '__main__':
  main( process_args() )
