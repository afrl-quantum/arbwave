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
from ctypes import byref, pointer, c_uint, c_ubyte, sizeof, addressof
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


  def __init__(self, options):
    self.options = options
    self.cmd = clib.comedi_cmd()
    self.chanlist = ( c_uint * 16 )()

    #/* Use extra to select waveform */
    fn = options.waveform
    if fn < 0 or fn >= len( dds_list ):
      print "Use the option '-w' to select another waveform."
      fn = 0
    dds_klass = dds_list[fn]

    if options.waveform_freq:
      self.waveform_frequency = options.waveform_freq

    self.dev = clib.comedi_open(options.filename)
    if not self.dev:
      print "error opening ", options.filename
      return -1;


    if options.subdevice < 0:
      options.subdevice = \
        clib.comedi_find_subdevice_by_type(self.dev, clib.COMEDI_SUBD_AO, 0)

    # ret = clib.comedi_reset( self.dev, options.subdevice )
    # if ret < 0:
    #   clib.comedi_perror('comedi_reset')
    #   raise OSError('comedi_reset failed')


    self.subdevice_flags = \
      clib.comedi_get_subdevice_flags(self.dev, options.subdevice)
    self.sampl_t = clib.sampl_t
    if self.subdevice_flags & clib.SDF_LSAMPL:
      self.sampl_t = clib.lsampl_t

    assert not (self.subdevice_flags & clib.SDF_FLAGS), 'flags per channel!'
    assert not (self.subdevice_flags & clib.SDF_MAXDATA), 'maxdata per channel!'
    assert not (self.subdevice_flags & clib.SDF_RANGETYPE), 'range per channel!'

    maxdata = clib.comedi_get_maxdata(self.dev, options.subdevice, options.channels[0])
    rng = clib.comedi_get_range(self.dev, options.subdevice, options.channels[0], options.range)

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
    self.cmd.scan_end_arg = len(options.channels)
    self.cmd.stop_src = clib.TRIG_NONE
    self.cmd.stop_arg = 0

    self.cmd.chanlist = self.chanlist
    self.cmd.chanlist_len = len(options.channels)

    aref = arefs[ options.aref ]
    for i,c in izip( xrange(len(options.channels)), options.channels ):
      self.chanlist[i] = clib.CR_PACK(c, options.range, aref)
  
    self.dds = dds_klass(
      self.amplitude, self.offset, self.waveform_frequency, options.freq )

    if options.verbose:
      print 'cmd: ', self.cmd

    err = clib.comedi_command_test(self.dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command_test")
      return 1

    err = clib.comedi_command_test(self.dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command_test")
      return 1

    size = clib.comedi_get_buffer_size( self.dev, options.subdevice )
    if options.verbose:
      print "buffer size is:", size

    # the following two integer projections are really unecessary, at least for
    # python 2.7, but are still written for clarity.  Probably necessar for
    # python3
    self.samples_per_channel \
      = int( int(size / sizeof(self.sampl_t)) / len(options.channels) )

    if options.n_samples:
      if options.n_samples > self.samples_per_channel:
        raise RuntimeError('Not enough memory for requested n_samples')
      self.samples_per_channel = options.n_samples

    shape = ( self.samples_per_channel, len(options.channels) )

    #print 'BUF_LEN, samples_per_channel, n_chan, shape: ', \
    #  self.BUF_LEN, self.samples_per_channel, len(options.channels), shape

    if options.oswrite:
      self.data = np.zeros( shape, dtype=self.sampl_t )

      def write_data( data, n ):
        buf = ( c_ubyte * n ).from_buffer( data )
        m = os.write( clib.comedi_fileno(self.dev), buf )
        if self.options.verbose:
          print "wrote {} out of {}".format(m, n)
        if m < 0:
          raise OSError('os write error')
        return m

    else:
      # The c version; we can cast directly
      #data = mmap(NULL, size, PROT_WRITE, MAP_SHARED, comedi_fileno(dev), 0)

      # the python version;  we must cast using ctypes
      self.mapped = mmap(clib.comedi_fileno(self.dev), size, prot=PROT_WRITE, flags=MAP_SHARED, offset=0)
      if not self.mapped:
        raise OSError( 'mmap: error!' ) # probably will already be raised
      self.data = np.ndarray( shape=shape, dtype=self.sampl_t,
                              buffer=self.mapped, order='C' )

      def write_data( data, n ):
        m = clib.comedi_mark_buffer_written(self.dev, options.subdevice, n)
        if self.options.verbose:
          print "Marked {} out of {}".format(m, n)
        if m < 0:
          clib.comedi_perror("comedi_mark_buffer_written")
          raise OSError('mark_buffer error')
        return m

    self.write_data = write_data


  def close(self):
    if hasattr( self, 'dev' ):
      if self.options.verbose:
        print 'closing comedi driver...'
      del self.data
      if not self.options.oswrite:
        self.mapped.close()
        del self.mapped
      clib.comedi_close(self.dev)
      del self.dev

  def __del__(self):
    self.close()


  @property
  def output_size(self):
    return ( self.samples_per_channel
           * len(self.options.channels)
           * sizeof(self.sampl_t) )

  def start(self):
    """
    Start the waveform
    """
    if self.options.verbose:
      print 'cmd: ', self.cmd
    err = clib.comedi_command(self.dev, self.cmd)
    if err < 0:
      clib.comedi_perror("comedi_command");
      return 1

    for i in xrange( len(self.options.channels) ):
      self.dds(self.data[:,i], self.samples_per_channel)

    n = self.output_size
    m = self.write_data( self.data, n )
    if m < n:
      print "failed to preload output buffer with", n, "bytes, is it too small?"
      print "See the --write-buffer option of comedi_config"
      raise OSError('--write-buffer ?')

    if self.options.verbose:
      print "m=",m

    ret = clib.comedi_internal_trigger(self.dev, self.options.subdevice, 0)
    if ret < 0:
      clib.comedi_perror('comedi_internal_trigger error')
      raise OSError('comedi_internal_trigger error: ')

  def wait(self):
    """
    wait while the waveform executes
    """
    try:
      time.sleep(100)
      # FIXME: this is not quite generic for both enough yet.  Need to call
      #   comedi_get_buffer_contents also.
      # total = 0
      #while True:
      #  self.dds(self.data,self.BUF_LEN)
      #  n = self.BUF_LEN * sizeof(self.sampl_t)
      #  while n>0:
      #    next_chunk = ( c_ubyte * n ) \
      #               .from_address( addressof(self.data)
      #                            + (self.BUF_LEN*sizeof(self.sampl_t)-n) )
      #    m=self.write_data(next_chunk,n)
      #    if self.options.verbose:
      #      print "m=",m
      #    n-=m
      #  total+=self.BUF_LEN;
      #  #print 'total: ', total
    except KeyboardInterrupt:
      pass


  def stop(self):
    """
    stop the waveform
    """
    if self.options.verbose:
      self.subdevice_flags = \
        clib.comedi_get_subdevice_flags(self.dev, self.options.subdevice)
      print 'before cancel flags:'
      print clib.extensions.subdev_flags.to_dict( self.subdevice_flags )

    # now cleanup
    clib.comedi_cancel( self.dev, self.options.subdevice )

    if self.options.verbose:
      self.subdevice_flags = \
        clib.comedi_get_subdevice_flags(self.dev, self.options.subdevice)
      print 'after cancel flags:'
      print clib.extensions.subdev_flags.to_dict( self.subdevice_flags )




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
    xt = np.r_[:self.WAVEFORM_LEN] * 2 * np.pi/self.WAVEFORM_LEN
    self.waveform = (ofs + amp*np.cos(xt)).round().astype(int)


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
      t=2*(1-float(i)/self.WAVEFORM_LEN)
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
  parser.add_argument( '-c', '--channels', nargs='+', type=int, default=[0] )
  parser.add_argument( '-a', '--aref',  choices=['ground', 'common'], default='ground' )
  parser.add_argument( '-r', '--range', type=int, default=0 )
  parser.add_argument( '-N', '--n_samples', type=int, default=0 )
  parser.add_argument( '-F', '--freq', type=float, default=1000. )
  parser.add_argument( '-w', '--waveform', type=int, default=0,
    help='\n\t'.join([ '{}: {}'.format(i,c.name)
           for i,c in zip(xrange(len(dds_list)), dds_list)]) )
  parser.add_argument( '-W', '--waveform_freq', nargs='?', type=float, default=0. )
  parser.add_argument( '-v', '--verbose', action='store_true' )
  parser.add_argument( '--oswrite', action='store_true' )
  return parser.parse_args()

def main(args):
  t = Test( process_args() )
  t.start()
  t.wait()
  t.stop()
  t.close()

if __name__ == '__main__':
  main( process_args() )
