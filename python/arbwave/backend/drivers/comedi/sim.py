# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level comedilib library.
"""

import comedi as clib
from ctypes import c_ubyte, cast, pointer, POINTER, addressof, c_uint, sizeof
from logging import log, debug, info, warn, error, critical, DEBUG
import os, re, time, tempfile
from importlib import reload
from itertools import chain
from ....tools.expand import expand_braces

from . import sim_device_routes


comedi_t_ptr = POINTER(clib.comedi_t)
def ctypes_ptr_to_int(self):
  """
  Simple class function to help turn comedi_t struct pointers into numbers

  To use:
    POINTER(comedi_t).__class__.__int__ = ctypes_ptr_to_int
  """
  if not self:
    return -1
  return addressof( self.contents ) - 1

def comedi_t_pointer_to_str(self):
  return 'comedi_t_ptr({})'.format( int(self) )

def ctypes_ptr_hash(self):
  return hash( int(self) )

def ctypes_ptr_eq(self, other):
  return int(self) == int(other)


def comedi_t_pointer(value):
  return cast( value+1, comedi_t_ptr )




def mk_crange(min,max,unit):
  r = clib.range()
  r.min = min
  r.max = max
  r.unit = unit
  return r

class BusyError(Exception): pass

class busy_marker(object):
  def __init__(self, subdev):
    self.subdev = subdev
  def __enter__(self):
    if self.subdev.flags & clib.SDF_BUSY:
      debug('comedi: Subdevice already busy')
      raise BusyError()
    self.subdev.flags |= clib.SDF_BUSY
  def __exit__(self,type,value,traceback):
    self.subdev.flags &= ~clib.SDF_BUSY


class SimSubDev(dict):
  SIMULATED_BUFFER_SIZE = 2**21 # in bytes

  def __init__(self, *a, **kw):
    super(SimSubDev,self).__init__(*a, **kw)
    self.__dict__ = self
    self.busy_body = busy_marker(self)

    # ensure that ranges are sorted correctly
    self.setdefault('type', clib.SUBD_UNUSED)
    self.setdefault('n_channels', 0)
    # FIXME:  replace this with a non static digital/analog representation
    self.setdefault('state', [0 for i in range(self.n_channels)])
    # for dio subdev:
    self.setdefault('ioconfig', [clib.INPUT for i in range(self.n_channels)])

    # for PFI, TRIG
    self.setdefault('routable', False)
    if self.routable:
      self.setdefault('routing', [-1 for i in range(self.n_channels)])

    self.setdefault('flags', 0)
    self.setdefault('cmd', dict())
    self.setdefault('ranges', dict())
    RI = self.ranges.items()
    self.ranges = list()

    # set the buffer file
    self.setdefault('max_buf_size', 2*self.SIMULATED_BUFFER_SIZE)
    if not self.flags & clib.SDF_CMD:
      # This subdevice is not for streaming--no buffer
      self.buf_file = self.buf_name = None
    else:
      buf_fd, self.buf_name = tempfile.mkstemp('.comedi_simbuf')
      self.buf_file = os.fdopen(buf_fd, 'r+')
      self.set_buffer_size(self.pop('buffer_sz', self.SIMULATED_BUFFER_SIZE))
      self.setdefault('convert_rng_ns',     (1000,0xffffffff))
      self.setdefault('scan_begin_rng_ns',  (1000,0xffffffff))

    self.buf_begin = self.buf_end = 0
    for u,r in RI:
      r = list(r)
      r.sort( key=lambda v : abs(v[0]) ) # sort ranges increasingly
      self.ranges += [ mk_crange(mn,mx,u) for mn,mx in r ]
    self.ranges = tuple( self.ranges ) # make immutable

  def __del__(self):
    self.cleanup()

  def cleanup(self):
    # clean up the buffer
    if self.buf_file:
      # must import these to make sure they exist upon exit
      import os, logging
      logging.debug('unlink(%s)', self.buf_name)
      self.buf_file.close()
      os.unlink(self.buf_name)
      self.buf_file = None

  def get_cmd_timing_constraints(self, scan_begin_src, scan_begin_min,
                                       convert_src, convert_min,
                                       chanlist, chanlist_len):
    if not self.flags & clib.SDF_CMD:
      return -1
    try:
      with self.busy_body:
        # our simulated hardware does not care how many channels or which
        # trigger modes are used
        scan_begin_min._obj.value = self.scan_begin_rng_ns[0]
        convert_min._obj.value    = self.convert_rng_ns[0]
        return 0
    except BusyError:
      return -1

  def command_test(self, command):
    if not self.flags & clib.SDF_CMD:
      return -1
    warn('comedi,sim:  comedi_command_test not simulated yet')
    return 0
    ## step 1: check if triggers are trivially valid
    #if (not command.start_src & self.cmd.start_src) or \
    #   (not command.scan_begin_src & self.cmd.scan_begin_src) or \
    #   (not command.convert_src & self.cmd.convert_src) or \
    #   (not command.scan_end_src & self.cmd.scan_end_src) or \
    #   (not command.stop_src & self.cmd.stop_src):
    #   return 1
    ## step 2: make sure trigger sources are unique and compatible
    #uniq = lambda x : (x and (x & (x-1)))
    #if not uniq(command.start_src) or \
    #   not uniq(command.scan_begin_src) or \
    #   not uniq(command.convert_src) or \
    #   not uniq(command.scan_end_src) or \
    #   not uniq(command.stop_src):

    ## step 3: check if arguments are valid
    #def lim(err, x, rng):
    #  x0 = min(rng[1], max(rng[0], x))
    #  return err | (x0!=x), x0
    #err, command.start_arg       = lim(0,  command.start_arg, self.start_rng_ns)
    #err, command.scan_begin_arg  = lim(err,command.scan_begin_arg, self.scan_begin_rng_ns)
    #err, command.convert_arg     = lim(err,command.convert_arg, self.convert_rng_ns)
    #err, command.scan_end_arg    = lim(err,command.scan_end_arg, self.scan_end_rng_ns)
    #err, command.stop_arg        = lim(err,command.stop_arg, self.stop_rng_ns)
    ## step 4: tweak arguments as necessary
    ## pass (not bothering with this)
    ## step 5: check if channels work together properly
    ## pass
    ## success:
    #return 0

  def fileno(self):
    if not self.flags & clib.SDF_CMD:
      return -1
    else:
      return self.buf_file.fileno()

  def find_range(self, channel, unit, min, max):
    assert min <= max, 'comedi_find_range:  min > max'
    # self.ranges is sorted increasingly
    ranges = [ r for r in self.ranges if r.unit == unit ]
    for i, r in zip( range(len(ranges)), ranges ):
      if r.min <= min and max <= r.max:
        return i
    return -1

  def get_maxdata(self, channel):
    return (2<<(self.bits-1)) - 1

  def maxdata_is_chan_specific(self):
    return 0

  def get_n_ranges(self, channel):
    return len( self.ranges ) # ignoring channel for now

  def get_range(self, channel, range):
    if range < len(self.ranges):
      return pointer(self.ranges[range])
    else:
      return POINTER(clib.range)()# return null pointer

  def range_is_chan_specific(self):
    return 0

  # AI functions
  def data_read(self, channel, range, aref, data):
    try:
      with self.busy_body:
        # dereference the pointer and set a value
        data._obj.value = self.state[channel]
        return 1
    except BusyError:
      return -1

  def data_read_n(self, channel, range, aref, data, n):
    try:
      with self.busy_body:
        # dereference the pointer and set a value
        data._obj[0:n] = [self.state[channel] for i in range(n)]
        return n
    except BusyError:
      return -1

  def data_read_delayed(self, channel, range, aref, data, nanosec):
    try:
      with self.busy_body:
        time.sleep( nanosec * 1e-9 )
        # dereference the pointer and set a value
        data._obj.value = self.state[channel]
        return 1
    except BusyError:
      return -1

  def data_read_hint(self, channel, range, aref):
    try:
      with self.busy_body:
        # hint taken
        return 0
    except BusyError:
      return -1

  # AO functions
  def data_write(self, channel, range, aref, data):
    try:
      with self.busy_body:
        self.state[channel] = data
        return 1 # success in any case!
    except BusyError:
      return -1

  # CMD functions
  def get_cmd_src_mask(self, cmd):
    if not self.flags & clib.SDF_CMD:
      return -1
    for a,v in self.cmd.items():
      setattr( cmd, a, v )
    return 0

  def get_buffer_size(self):
    if not self.flags & clib.SDF_CMD:
      return -1
    return os.path.getsize(self.buf_name)

  def set_buffer_size( self, size ):
    if not self.flags & clib.SDF_CMD:
      return -1
    size =  min(size, self.max_buf_size)
    self.buf_file.truncate( size )
    return size

  def get_buffer_contents(self):
    if not self.flags & clib.SDF_CMD:
      return -1
    return self.buf_end - self.buf_begin

  def get_buffer_offset(self):
    if not self.flags & clib.SDF_CMD:
      return -1
    return self.buf_begin

  def mark_buffer_read(self, num_bytes):
    if not self.flags & clib.SDF_CMD:
      return -1
    if self.type not in [clib.SUBD_AI,
                         clib.SUBD_DI,
                         clib.SUBD_DIO]:
      return -1
    avail = self.get_buffer_contents()
    if num_bytes > avail:
      return -1
    self.buf_begin += num_bytes
    return num_bytes

  def mark_buffer_written(self, num_bytes):
    if not self.flags & clib.SDF_CMD:
      return -1
    if self.type not in [clib.SUBD_AO,
                         clib.SUBD_DO,
                         clib.SUBD_DIO]:
      error('comedi.mark_buffer_written(%s): wrong buffer type', self.type )
      return -1
    avail = self.get_buffer_contents()
    if num_bytes > avail:
      error('comedi.mark_buffer_written(%s): no mem available', self.type )
      return -1
    self.buf_begin += num_bytes
    return num_bytes

  def apply_calibration(self, channel, range, aref, file_path):
    raise NotImplementedError('not simulated yet')

  def apply_parsed_calibration(self, channel, range, aref, calib):
    raise NotImplementedError('not simulated yet')



  # Digital I/O
  def dio_bitfield2(self, write_mask, bits, base_channel):
    try:
      with self.busy_body:
        for i, ch in zip( range(8*sizeof(c_uint)),
                          range( base_channel, self.n_channels ) ):
          if write_mask & (1 << i):
            self.state[ch] = bits._obj.value & ( 1 << i )
          bits._obj.value &= ~( 1 << i ) # clear bit
          bits._obj.value |= bool(self.state[ch]) << i # write bit
        return 0
    except BusyError:
      return -1

  def dio_config(self, channel, direction):
    self.ioconfig[channel] = direction
    return 0

  def dio_get_config(self, channel, direction):
    direction._obj.value = self.ioconfig[channel]
    return 0

  def dio_read( self, channel, bit ):
    bit._obj.value = self.state[channel]
    return 1

  def dio_write( self, channel, bit ):
    self.state[channel] = bit
    return 1


  def set_routing(self, channel, routing):
    if not self.routable:
      return -1
    self.routing[channel] = routing
    return 0

  def get_routing(self, channel, routing):
    if (not self.routable) or self.routing[channel] < 0:
      return -1
    routing._obj.value = self.routing[channel]
    return 0




class SimCard(object):
  driver  = None
  board   = None
  subdevs = dict()
  def __init__(self):
    super(SimCard,self).__init__()
    # initialize subdevs...
    self.subdevs = { i:SimSubDev(D) for i,D in self.subdevs.items() }
    self.routes = sim_device_routes.get(self.board)
    self.current_routes = set()

    # set the current streaming read subdevice to the first one
    self.current_read_subdevice = self.find_subdevice_by_type(
      (clib.SUBD_AI, clib.SUBD_DI, clib.SUBD_DIO), 0,
      flagmask=clib.SDF_CMD | clib.SDF_CMD_READ,
    )

    # set the current streaming write subdevice to the first one
    self.current_write_subdevice = self.find_subdevice_by_type(
      (clib.SUBD_AO, clib.SUBD_DO, clib.SUBD_DIO), 0,
      flagmask=clib.SDF_CMD | clib.SDF_CMD_WRITE,
    )

    # set the current subdevice (a hack for fileno)
    if self.current_read_subdevice >= 0:
      self.current_subdevice = self.current_read_subdevice
    else:
      self.current_subdevice = self.current_write_subdevice

  def __del__(self):
    self.cleanup()

  def cleanup(self):
    # must import to make sure it exists upon exit
    import logging
    for k, s in self.subdevs.items():
      logging.debug('cleanup subdev %d', k)
      s.cleanup()

  def __getitem__(self,i):
    """Quick method of indexing the subdevice"""
    return self.subdevs[i]

  def lock(self, subdevice):
    if self.subdevs[subdevice].flags & clib.SDF_LOCKED:
      return -1
    self.subdevs[subdevice].flags |= clib.SDF_LOCKED | clib.SDF_LOCK_OWNER
    return 0

  def unlock(self, subdevice):
    if not self.isLockedBySelf(subdevice):
      return -1
    self.subdevs[subdevice].flags &= ~(clib.SDF_LOCKED | clib.SDF_LOCK_OWNER)
    return 0

  def isLockedBySelf(self, subdevice):
    lock_owned = (clib.SDF_LOCKED | clib.SDF_LOCK_OWNER)
    return (self.subdevs[subdevice].flags & lock_owned) == lock_owned

  def find_subdevice_by_type(self, typ, start_subdevice, flagmask=0):
    if type(typ) not in [ list, tuple, dict ]:
      typ = [ typ ]
    if start_subdevice < 0:
      raise OverflowError('comedi_find_subdevice_by_type: start_subdevice >=0!')
    k = [ k for k,v in self.subdevs.items()
          if v.type in typ and (v.flags & flagmask)==flagmask ]
    if len(k) == 0 or start_subdevice > max(k):
      log(DEBUG-1,'returning subdev: -1')
      return -1
    while start_subdevice not in k:
      start_subdevice += 1
    log(DEBUG-1,'returning subdev: %d', start_subdevice)
    return start_subdevice

  def get_read_subdevice(self):
    """
    The function comedi_get_read_subdevice() returns the index of the subdevice
    whose streaming input buffer is currently accessible through the device
    device . If there is no such subdevice, -1 is returned.
    """
    self.current_subdevice = self.current_read_subdevice
    return self.current_read_subdevice

  def set_read_subdevice(self, subdevice):
    """
    The function comedi_set_read_subdevice() sets subdevice as the current
    "read" subdevice if the subdevice supports streaming input commands.
    No action is performed if subdevice is already the current "read" subdevice.
    Changes are local to the open file description for this device and have no
    effect on other open file descriptions for the underlying
    device node.

    On success, 0 is returned. On failure, -1 is returned.
    """
    # We'll simply search from the specified subdev and test if we found it
    read_subdevice = self.find_subdevice_by_type(
      (clib.SUBD_AI, clib.SUBD_DI, clib.SUBD_DIO), subdevice,
      flagmask=clib.SDF_CMD | clib.SDF_CMD_READ,
    )
    if read_subdevice == subdevice:
      self.current_subdevice = self.current_read_subdevice = read_subdevice
      return 0
    return -1

  def get_write_subdevice(self):
    """
    The function comedi_get_write_subdevice() returns the index of the subdevice
    whose streaming output buffer is currently accessible through this
    (simulated) card. If there is no such subdevice, -1 is returned.
    """
    self.current_subdevice = self.current_write_subdevice
    return self.current_write_subdevice

  def set_write_subdevice(self, subdevice):
    """
    The function comedi_set_write_subdevice() sets subdevice as the current
    "write" subdevice if the subdevice supports streaming output commands.
    No action is performed if subdevice is already the current "write"
    subdevice.
    Changes are local to the open file description for this device and have no
    effect on other open file descriptions for the underlying device node.

    On success, 0 is returned. On failure, -1 is returned.
    """
    # We'll simply search from the specified subdev and test if we found it
    write_subdevice = self.find_subdevice_by_type(
      (clib.SUBD_AO, clib.SUBD_DO, clib.SUBD_DIO), subdevice,
      flagmask=clib.SDF_CMD | clib.SDF_CMD_WRITE,
    )
    if write_subdevice == subdevice:
      self.current_subdevice = self.current_write_subdevice = write_subdevice
      return 0
    return -1

  def fileno(self):
    """
    get file descriptor for open Comedilib device.

    This simulated interface returns the filepointer to the current write/read
    subdevice.  Which one is returned is somewhat arbitrary, but will be the
    last one that was set explicitly through comedi_set_[read|write]_subdevice,
    or the read subdevice.
    This operates in this fashion since we cannot hijack mmap or os.write like
    comedi actually does.
    """
    if self.current_subdevice not in self.subdevs:
      return -1
    return self.subdevs[self.current_subdevice].fileno()

  def test_route(self, source, destination):
    if source in self.routes and destination in self.routes[source]:
      if (source,destination) in self.current_routes:
        return 1
      return 0
    return -1

  def connect_route(self, source, destination):
    test = self.test_route(source, destination)
    if test in [-1, 1]:
      return -1
    self.current_routes.add((source,destination))
    return 0

  def disconnect_route(self, source, destination):
    test = self.test_route(source, destination)
    if test in [-1, 0]:
      return -1
    self.current_routes.remove((source,destination))
    return 0

  def get_routes(self, routelist, len_routelist):
    if (not routelist) or len_routelist == 0:
      # just return the number of routes
      return sum([len(v) for k,v in self.routes.items()])

    S = set(chain(*[{(k,vi) for vi in v} for k,v in self.routes.items()]))
    for route,p in zip(S,routelist[:len_routelist]):
      p.source, p.destination = route
    return min(len(S), len(routelist), len_routelist)


class PXI_6733(SimCard):
  driver = 'ni_pcimio'
  board = 'pxi-6733'
  subdevs = {
    1 : dict( type=clib.SUBD_AO, n_channels=8,
      bits=16,
      flags= clib.SDF_CMD       |
             clib.SDF_CMD_WRITE |
             clib.SDF_DEGLITCH  |
             clib.SDF_GROUND    |
             clib.SDF_WRITEABLE,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=clib.TRIG_NOW,
               data=None,
               data_len=0,
               flags=clib.CMDF_WRITE,
               scan_begin_arg=0,
               scan_begin_src=clib.TRIG_TIMER|clib.TRIG_EXT,
               scan_end_arg=0,
               scan_end_src=clib.TRIG_COUNT,
               start_arg=0,
               start_src=clib.TRIG_INT|clib.TRIG_EXT,
               stop_arg=0,
               stop_src=clib.TRIG_COUNT|clib.TRIG_NONE,
               subdev=1,
      ),
      convert_rng_ns      = (0,0),
      scan_begin_rng_ns   = (1000,0xffffffff),
      ranges={ clib.UNIT_volt : ( (-10,10), )  },
    ),
    # subdev 7 represents PFI lines
    7 : dict( type=clib.SUBD_DIO, n_channels=10,
      bits=1,
      routable=True,
      flags= clib.SDF_INTERNAL  |
             clib.SDF_READABLE  |
             clib.SDF_WRITEABLE,
      ranges={ clib.UNIT_none : ( (0,1), )  },
    ),
    # subdev 10 represents RTSI lines
    10 : dict( type=clib.SUBD_DIO, n_channels=8,
      bits=1,
      routable=True,
      flags= clib.SDF_INTERNAL  |
             clib.SDF_READABLE  |
             clib.SDF_WRITEABLE,
      ranges={ clib.UNIT_none : ( (0,1), )  },
    ),
  }

def subdev_replace_n_channels(S, N):
  S[1]['n_channels'] = N
  return S

class PXI_6723(PXI_6733):
  board = 'pci-6723'
  subdevs = subdev_replace_n_channels(PXI_6733.subdevs.copy(), 32)

class PCI_6229(SimCard):
  driver = 'ni_pcimio'
  board = 'pci-6229'
  subdevs = {
    1 : dict( type=clib.SUBD_AO, n_channels=4,
      bits=16,
      flags= clib.SDF_CMD       |
             clib.SDF_CMD_WRITE |
             clib.SDF_DEGLITCH  |
             clib.SDF_GROUND    |
             clib.SDF_WRITEABLE |
             clib.SDF_SOFT_CALIBRATED,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=clib.TRIG_NOW,
               data=None,
               data_len=0,
               flags=clib.CMDF_WRITE,
               scan_begin_arg=0,
               scan_begin_src=clib.TRIG_TIMER|clib.TRIG_EXT,
               scan_end_arg=0,
               scan_end_src=clib.TRIG_COUNT,
               start_arg=0,
               start_src=clib.TRIG_INT|clib.TRIG_EXT,
               stop_arg=0,
               stop_src=clib.TRIG_COUNT|clib.TRIG_NONE,
               subdev=1,
      ),
      convert_rng_ns      = (0,0),
      scan_begin_rng_ns   = (1200,0xffffffff),
      ranges={ clib.UNIT_volt : ( (-10,10), (-2,2), (-1,1) )  },
    ),
    2 : dict( type=clib.SUBD_DIO, n_channels=32,
      bits=1,
      flags= clib.SDF_CMD       |
             clib.SDF_CMD_WRITE |
             clib.SDF_READABLE  |
             clib.SDF_WRITEABLE |
             clib.SDF_LSAMPL,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=clib.TRIG_NOW,
               data=None,
               data_len=0,
               flags=clib.CMDF_WRITE,
               scan_begin_arg=0,
               scan_begin_src=clib.TRIG_TIMER|clib.TRIG_EXT,
               scan_end_arg=0,
               scan_end_src=clib.TRIG_COUNT,
               start_arg=0,
               start_src=clib.TRIG_INT,
               stop_arg=0,
               stop_src=clib.TRIG_COUNT|clib.TRIG_NONE,
               subdev=2,
      ),
      convert_rng_ns      = (0,0),
      scan_begin_rng_ns   = (1000,0xffffffff),
      ranges={ clib.UNIT_volt : ( (0,5), ) },
    ),
    # subdev 7 represents PFI lines
    7 : dict( type=clib.SUBD_DIO, n_channels=10,
      bits=1,
      routable=True,
      flags= clib.SDF_INTERNAL  |
             clib.SDF_READABLE  |
             clib.SDF_WRITEABLE,
      ranges={ clib.UNIT_none : ( (0,1), )  },
    ),
    # subdev 10 represents RTSI lines
    10 : dict( type=clib.SUBD_DIO, n_channels=8,
      bits=1,
      routable=True,
      flags= clib.SDF_INTERNAL  |
             clib.SDF_READABLE  |
             clib.SDF_WRITEABLE,
      ranges={ clib.UNIT_none : ( (0,1), )  },
    ),
  }


class ComediSim(object):
  def __init__(self, auto_inject=True):
    self.cards = dict()
    if auto_inject:
      self.inject_into_clib()

  def inject_into_clib(self):
    # these have to bound to the class
    comedi_t_ptr.__int__ = ctypes_ptr_to_int
    comedi_t_ptr.__hash__ = ctypes_ptr_hash
    comedi_t_ptr.__repr__ = comedi_t_pointer_to_str
    comedi_t_ptr.__eq__ = ctypes_ptr_eq

    self.cards = {
      comedi_t_pointer(0) : PXI_6733(),
      comedi_t_pointer(1) : PXI_6723(),
      comedi_t_pointer(2) : PCI_6229(),
    }
    assert -1 not in [ int(i) for i in self.cards ]

    debug( 'comedi.sim:  injecting simulated library into c-interface' )
    import_funcs = [ f for f in dir(self) if f.startswith('comedi_')]
    for f in import_funcs:
      setattr( clib, f, getattr(self,f) ) # set full name
      setattr( clib, f[len('comedi_'):], getattr(self,f) ) # set shortened name

    #store pointer to this simulation instance
    clib.sim = self

  def remove_from_clib(self):
    if hasattr( comedi_t_ptr, '__int__' ):
      # must import this to make sure it exists upon exit
      import logging
      logging.debug('comedi.sim:  removing injected simulated library from c-interface')
      # delete cards and associated buffers
      for k, c in self.cards.items():
        logging.debug('comedi.sim: cleaning up card(%d)', k)
        c.cleanup()
      del self.cards
      self.cards = dict()

      # delete hacks to comedi_t_ptr type
      del comedi_t_ptr.__int__
      del comedi_t_ptr.__hash__
      del comedi_t_ptr.__repr__
      del comedi_t_ptr.__eq__
      reload(clib)

  def __getitem__(self, i):
    """Quick access to cards by index or by comedi_t_ptr"""
    if type(i) is int:
      return self[ comedi_t_pointer(i) ]
    return self.cards[i]

  def glob_device_files(self):
    dev_numbers = [ int(p) for p in self.cards ]
    mn,mx = min(dev_numbers), max(dev_numbers)
    return expand_braces('/dev/comedi{{{}..{}}}'.format(mn,mx))

  def comedi_open(self, filename):
    debug('comedi_open(%s)', filename)
    m = re.match( '/dev/comedi(?P<card_number>[0-9]+)$', filename )
    if not m:
      return comedi_t_pointer(-1)

    card_ptr = comedi_t_pointer( int(m.group('card_number')) )

    if card_ptr not in self.cards:
      return comedi_t_pointer(-1)

    return card_ptr


  def comedi_close(self, fp):
    debug('comedi_close(%d)', fp)
    if fp not in self.cards:
      return -1

    card = self.cards[fp]
    for sd in card.subdevs:
      if card.isLockedBySelf(sd):
        self.comedi_unlock(card,sd)
    return 0


  def comedi_fileno(self, fp):
    """
    get file descriptor for open Comedilib device.

    This simulated interface returns the filepointer to the current write/read
    subdevice.  Which one is returned is somewhat arbitrary, but will be the
    last one that was set explicitly through comedi_set_[read|write]_subdevice,
    or the read subdevice.
    This operates in this fashion since we cannot hijack mmap or os.write like
    comedi actually does.
    """
    debug('comedi_fileno(%d)', fp)
    if not fp or fp not in self.cards:
      return -1
    return self[fp].fileno()


  def comedi_get_version_code(self, fp):
    """
    Comedi version code.

    we'll just return a lame version for all kernel modules
    """
    debug('comedi_get_version_code(%d)', fp)
    return 0x1


  def comedi_set_read_subdevice(self, subdevice):
    """
    The function comedi_set_read_subdevice() sets subdevice as the current
    "read" subdevice if the subdevice supports streaming input commands.
    No action is performed if subdevice is already the current "read" subdevice.
    Changes are local to the open file description for this device and have no
    effect on other open file descriptions for the underlying
    device node.

    On success, 0 is returned. On failure, -1 is returned.
    """
    debug('comedi_set_read_subdevice(%d, %d)', fp, subdevice)
    return self[fp].set_read_subdevice(subdevice)


  def comedi_get_read_subdevice(self, fp):
    """
    The function comedi_get_read_subdevice() returns the index of the subdevice
    whose streaming input buffer is currently accessible through the (simulated)
    card . If there is no such subdevice, -1 is returned.
    """
    debug('comedi_get_read_subdevice(%d)', fp)
    return self[fp].get_read_subdevice()


  def comedi_set_write_subdevice(self, fp, subdevice):
    """
    The function comedi_set_write_subdevice() sets subdevice as the current
    "write" subdevice if the subdevice supports streaming output commands.
    No action is performed if subdevice is already the current "write"
    subdevice.
    Changes are local to the open file description for this device and have no
    effect on other open file descriptions for the underlying device node.

    On success, 0 is returned. On failure, -1 is returned.
    """
    debug('comedi_set_write_subdevice(%d, %d)', fp, subdevice)
    return self[fp].set_write_subdevice(subdevice)


  def comedi_get_write_subdevice(self, fp):
    """
    The function comedi_get_write_subdevice() returns the index of the subdevice
    whose streaming output buffer is currently accessible through the
    (simulated) card. If there is no such subdevice, -1 is returned.
    """
    debug('comedi_get_write_subdevice(%d)', fp)
    return self[fp].get_write_subdevice()


  def comedi_get_n_subdevices(self, fp):
    debug('comedi_get_n_subdevices(%d)', fp)
    return len( self[fp].subdevs )


  def comedi_get_subdevice_type(self, fp, sub):
    debug('comedi_get_subdevice_type(%d, %d)', fp, sub)
    return self[fp][sub].type

  def comedi_find_subdevice_by_type(self, fp, typ, start_subdevice):
    debug('comedi_find_subdevice_by_type(%d, %d, %d)', fp,typ,start_subdevice)
    if fp not in self.cards: return -1
    return self[fp].find_subdevice_by_type(typ, start_subdevice)

  def comedi_get_subdevice_flags(self, fp, sub):
    debug('comedi_get_subdevice_flags(%d, %d)', fp, sub)
    if fp not in self.cards: return -1
    return self[fp][sub].flags

  def comedi_get_n_channels(self, fp, sub):
    debug('comedi_get_n_channels(%d, %d)', fp, sub)
    if fp not in self.cards: return -1
    return self[fp][sub].n_channels

  def comedi_get_driver_name(self, fp):
    debug('comedi_get_driver_name(%d)', fp)
    return self[fp].driver.encode()

  def comedi_get_board_name(self, fp):
    debug('comedi_get_board_name(%d)', fp)
    return self[fp].board.encode()

  def comedi_cancel(self, fp, sub):
    debug('comedi_cancel(%d, %d)', fp, sub)
    self[fp][sub].flags &= ~( clib.SDF_BUSY
                            | clib.SDF_BUSY_OWNER
                            | clib.SDF_RUNNING )
    return 0

  def comedi_lock(self, fp, sub):
    debug('comedi_lock(%d, %d)', fp, sub)
    return self[fp].lock(sub)

  def comedi_unlock(self, fp, sub):
    debug('comedi_unlock(%d, %d)', fp, sub)
    return self[fp].unlock(sub)

  def comedi_find_range(self, fp, sub, channel, unit, min, max):
    debug('comedi_find_range(%d,%d,%d,%d,%g,%g)', fp,sub,channel,unit,min,max)
    return self[fp][sub].find_range(channel, unit, min, max)

  def comedi_get_maxdata(self, fp, sub, channel):
    debug('comedi_get_maxdata(%d,%d,%d)', fp,sub,channel)
    return self[fp][sub].get_maxdata(channel)

  def comedi_get_n_ranges(self, fp, sub, channel):
    debug('comedi_get_n_ranges(%d,%d,%d)', fp,sub,channel)
    return self[fp][sub].get_n_ranges(channel)

  def comedi_get_range(self, fp, sub, channel, range):
    debug('comedi_get_range(%d,%d,%d,%s)', fp,sub,channel, range)
    return self[fp][sub].get_range(channel, range)

  def comedi_maxdata_is_chan_specific(self, fp, sub):
    debug('comedi_maxdata_is_chan_specific(%d,%d)', fp,sub)
    return self[fp][sub].maxdata_is_chan_specific()

  def comedi_range_is_chan_specific(self, fp, sub):
    debug('comedi_range_is_chan_specific(%d,%d)', fp,sub)
    return self[fp][sub].range_is_chan_specific()


  # AI functions
  def comedi_data_read(self, fp, subdev, channel, range, aref, data):
    debug('comedi_data_read(%d, %d, %d, %d, %d, %d)',
          fp, subdev, channel, range, aref, data)
    return self[fp][subdev].data_read(channel, range, aref, data)

  def comedi_data_read_n(self, fp, subdev, channel, range, aref, data, n):
    debug('comedi_data_read_n(%d, %d, %d, %d, %d, %d, %d)',
          fp, subdev, channel, range, aref, data, n)
    return self[fp][subdev].data_read_n(channel, range, aref, data, n)

  def comedi_data_read_delayed(self, fp, subdev, channel,
                               range, aref, data, nanosec):
    """
    read single sample from channel after delaying for specified settling time
    """
    debug('comedi_data_read_delayed(%d, %d, %d, %d, %d, %d, %d)',
          fp, subdev, channel, range, aref, data, nanosec)
    return self[fp][subdev] \
      .data_read_delayed(channel, range, aref, data, nanosec)

  def comedi_data_read_hint(self, fp, subdev, channel, range, aref):
    """
    tell driver which channel/range/aref you are going to read from next
    """
    debug('comedi_data_read_hint(%d, %d, %d, %d, %d)',
          fp, subdev, channel, range, aref)
    return self[fp][subdev].data_read_hint(channel, range, aref)


  # AO functions
  def comedi_data_write(self, fp, subdev, channel, range, aref, data):
    """
    Writes a single sample on the channel that is specified by the Comedi
    (simulated) card, the subdevice subdevice, and the channel channel. If
    appropriate, the card is configured to use range specification range and
    analog reference type aref. Analog reference types that are not supported by
    the card are silently ignored.

    The function comedi_data_write() writes the data value specified by the
    parameter data to the specified channel.
    """
    debug('comedi_data_write(%d, %d, %d, %d, %d, %d)',
          fp, subdev, channel, range, aref, data)
    return self[fp][subdev].data_write(channel, range, aref, data)


  # CMD functions
  def comedi_get_cmd_src_mask(self, fp, subdev, cmd):
    debug('comedi_get_cmd_src_mask(%d, %d, %s)', fp, subdev, cmd)
    if fp not in self.cards: return -1
    return self[fp][subdev].get_cmd_src_mask(cmd)

  def comedi_internal_trigger(self, fp, subdevice, trig_num=0):
    debug('comedi_internal_trigger(%d, %d, %s)', fp, subdevice, trig_num)
    return 0

  def comedi_do_insn(self, fp, instruction):
    i = instruction
    debug('comedi_do_insn(%d, %s)', fp, i)
    if ( i.insn == clib.INSN_WRITE ):
      C,R,A = ( f(i.chanspec) for f in [clib.CR_CHAN,clib.CR_RANGE,clib.CR_AREF] )
      for j in range(i.n):
        self[fp][i.subdev].data_write(C,R,A,i.data[j])
      return i.n
    if ( i.insn == clib.INSN_READ ):
      C,R,A = ( f(i.chanspec) for f in [clib.CR_CHAN,clib.CR_RANGE,clib.CR_AREF] )
      self[fp][i.subdev].data_read_n(C,R,A,i.data,i.n)
      return i.n
    if ( i.insn == clib.INSN_BITS ):
      return -1
    if ( i.insn == clib.INSN_GTOD ):
      assert i.n == 2, 'INSN_GTOD requires buffer of len=2'
      t = time.time()
      i.data[0] = int(t)
      i.data[1] = int( ( t - int(t)) * 1e6 )
      return 0
    if ( i.insn == clib.INSN_WAIT ):
      assert i.n == 1, 'INSN_WAIT requires buffer of len=1'
      time.sleep(i.data[0])
      return 0

    raise NotImplementedError(
      'command instruction ({}) not simulated yet'.format(i.insn))

  def comedi_do_insnlist(self, fp, instruction_list):
    debug('comedi_do_insnlist(%d, %s)', fp, instruction_list)
    successes = 0
    for i in range(instruction_list.n_insns):
      ri = self.comedi_do_insn( fp, instruction_list.insns[i] )
      if ri >= 0: successes += 1
      else: break
    return successes if successes > 0 else -1

  def comedi_command(self, fp, command):
    debug('comedi_command(%d, %s)', fp, command)
    sdev = self[fp][command.subdev]
    if sdev.flags & clib.SDF_BUSY:
      return -1

    # mark buffer end
    sdev.buf_begin = 0
    sdev.buf_end = sdev.get_buffer_size()

    # make busy, make running, make self busy_owner
    sdev.flags |= clib.SDF_BUSY        \
                | clib.SDF_BUSY_OWNER  \
                | clib.SDF_RUNNING
    # if not continuous, wait a tad, then set not running
    if command.stop_src != clib.TRIG_NONE:
      time.sleep(10e-3)
      sdev.flags &= ~clib.SDF_RUNNING
    return 0


  def comedi_command_test(self, fp, command):
    """
    Tests the command structure pointed to by the parameter command and returns
    an integer describing the testing stages that were successfully passed. In
    addition, if elements of the comedi_cmd structure are invalid, they may be
    modified. Source elements are modified to remove invalid source triggers.
    Argument elements are adjusted or rounded to the nearest valid value.
    """
    # This function is necessary to simulate in order to provide a means for
    # arbwave to discover the limits on clocked devices.  It might be
    # preferable, in the future, to implement a specific function in the comedi
    # kernel drivers to return the limits.
    debug('comedi_command_test(%d, %s)', fp, command)
    if command.subdev not in self[fp].subdevs:
      return -1;
    return self[fp][command.subdev].command_test(command)


  def comedi_get_buffer_contents(self, fp, subdevice):
    """
    The function comedi_get_buffer_contents() is used on a subdevice that has a
    Comedi command in progress. The number of bytes that are available in the
    streaming buffer is returned. If there is an error, -1 is returned.
    """
    debug('comedi_get_buffer_contents(%d, %d)', fp, subdevice)
    return self[fp][subdevice].get_buffer_contents()

  def comedi_get_buffer_offset(self, fp, subdevice):
    """
    The function comedi_get_buffer_offset() is used on a subdevice that has a
    Comedi command in progress. This function returns the offset in bytes of the
    read pointer in the streaming buffer.  This offset is only useful for memory
    mapped buffers. If there is an error, -1 is returned.
    """
    debug('comedi_get_buffer_offset(%d, %d)', fp, subdevice)
    return self[fp][subdevice].get_buffer_offset()

  def comedi_get_buffer_size(self, fp, subdevice):
    """
    The function comedi_get_buffer_size() returns the size (in bytes) of the
    streaming buffer for the subdevice specified by card and subdevice. On
    error, -1 is returned.
    """
    debug('comedi_get_buffer_size(%d, %d)', fp, subdevice)
    return self[fp][subdevice].get_buffer_size()

  def comedi_set_buffer_size(self, fp, subdevice, size):
    debug('comedi_set_buffer_size(%d, %d, %d)', fp, subdevice, size)
    self[fp][subdevice].set_buffer_size(size)

  def comedi_set_max_buffer_size(self, fp, subdevice, max_size):
    """Requires privileged execution."""
    debug('comedi_set_max_buffer_size(%d, %d, %d)', fp, subdevice, max_size)
    self[fp][subdevice].max_buf_size = max_size

  def comedi_get_max_buffer_size(self, fp, subdevice):
    debug('comedi_get_max_buffer_size(%d, %d)', fp, subdevice)
    return self[fp][subdevice].max_buf_size

  def comedi_get_cmd_generic_timed(self, fp, subdevice, command,
                                   chanlist_len, scan_period_ns):
    debug('comedi_get_cmd_generic_timed(%d, %d, %s, %d, %d)',
          fp, subdevice, command, chanlist_len, scan_period_ns)
    raise NotImplementedError('not simulated yet')

  def comedi_mark_buffer_read(self, fp, subdevice, num_bytes):
    """
    The function comedi_mark_buffer_read() is used on a subdevice that has a
    Comedi input command in progress. It should only be used if you are using a
    mmap() mapping to read data from Comedi's buffer.
    """
    debug('comedi_mark_buffer_read(%d, %d, %d)', fp, subdevice, num_bytes)
    return self[fp][subdevice].mark_buffer_read( num_bytes )

  def comedi_mark_buffer_written(self, fp, subdevice, num_bytes):
    debug('comedi_mark_buffer_written(%d, %d, %d)', fp, subdevice, num_bytes)
    return self[fp][subdevice].mark_buffer_written( num_bytes )


  def comedi_poll(self, fp, subdevice):
    debug('comedi_poll(%d, %d)', fp, subdevice)
    # we'll just return what is available now; no actual dma
    return self[fp][subdevice].get_buffer_contents()


  # calibration
  def comedi_apply_calibration(self, fp, sub, channel, range, aref,
                               file_path):
    return self[fp][sub] \
      .apply_calibration(channel, range, aref, file_path)

  def comedi_apply_parsed_calibration(self, fp, sub, channel, range,
                                      aref, calibration):
    return self[fp][sub] \
      .apply_parsed_calibration(channel, range, aref, calibration)

  def comedi_get_default_calibration_path(self, fp):
    return self[fp].get_default_calibration_path()

  def comedi_get_hardcal_converter(self, fp, sub, channel,
                                   range, direction, converter):
    return self[fp][sub] \
      .get_hardcal_converter(channel, range, direction, converter)

  def comedi_get_softcal_converter(self, sub, channel,
                                   range, direction, parsed_calibration,
                                   converter):
    return self[fp][sub] \
      .get_softcal_converter(channel, range, direction,
                             parsed_calibration, converter)


  # Digital I/O
  def comedi_dio_bitfield2(self, fp, sub, write_mask, bits, base_channel):
    debug( 'comedi_dio_bitfield2(%d, %d, %d, %s, %d)',
           fp, sub, write_mask, bits, base_channel )
    return self[fp][sub].dio_bitfield2(write_mask, bits, base_channel)

  def comedi_dio_config(self, fp, sub, channel, direction):
    debug('comedi_dio_config(%d, %d, %d, %d)', fp,sub,channel, direction)
    return self[fp][sub].dio_config(channel, direction)

  def comedi_dio_get_config(self, fp, sub, channel, direction):
    debug('comedi_dio_get_config(%d, %d, %d, %d)', fp, sub, channel, direction)
    return self[fp][sub].dio_get_config(channel, direction)

  def comedi_dio_read(self, fp, sub, channel, bit):
    debug('comedi_dio_read(%d, %d, %d, %d)', fp, sub, channel, bit)
    return self[fp][sub].dio_read(channel, bit)

  def comedi_dio_write(self, fp, sub, channel, bit):
    debug('comedi_dio_write(%d, %d, %d, %d)', fp, sub, channel, bit)
    return self[fp][sub].dio_write(channel, bit)


  # Extensions
  def comedi_arm(self, fp, sub, source):
    debug('comedi_arm(%d, %d, %d)', fp, sub, source)
    # nothing to really arm...
    #return self[fp][sub].comedi_arm(source)
    return 0

  def comedi_get_clock_source(self, fp, sub, channel, clock, period_ns):
    debug('comedi_get_clock_source(%d, %d, %d, %d, %d)', fp, sub, channel,
          clock, period_ns)
    return self[fp][sub].comedi_get_clock_source(channel, clock, period_ns)

  def comedi_get_gate_source(self, fp, sub, channel, gate_index,
                             gate_source):
    debug('comedi_get_gate_source(%d, %d, %d, %d, %d)', fp, sub, channel,
          gate_index, gate_source)
    return self[fp][sub].comedi_get_gate_source(channel, gate_index, gate_source)

  def comedi_get_hardware_buffer_size(self, fp, sub, direction):
    debug('comedi_get_hardware_buffer_size(%d, %d, %d)', fp, sub, direction)
    return self[fp][sub].comedi_get_hardware_buffer_size(direction)

  def comedi_get_routing(self, fp, sub, channel, routing):
    debug('comedi_get_routing(%d, %d, %d, %s)', fp, sub, channel, routing)
    return self[fp][sub].get_routing(channel, routing)

  def comedi_reset(self, fp, sub):
    debug('comedi_reset(%d, %d)', fp, sub)
    return self[fp][sub].comedi_reset()

  def comedi_set_clock_source(self, fp, sub, channel, clock, period_ns):
    debug('comedi_set_clock_source(%d, %d, %d, %d, %d)', fp, sub, channel,
          clock, period_ns)
    return self[fp][sub].comedi_set_clock_source(channel, clock, period_ns)

  def comedi_set_counter_mode(self, fp, sub, channel, mode):
    debug('comedi_set_counter_mode(%d, %d, %d, %d)', fp, sub, channel, mode)
    return self[fp][sub].comedi_set_counter_mode(channel, mode)

  def comedi_set_filter(self, fp, sub, channel, filter):
    debug('comedi_set_filter(%d, %d, %d, %d)', fp, sub, channel, filter)
    return self[fp][sub].comedi_set_filter(channel, filter)

  def comedi_set_gate_source(self, fp, sub, channel, gate_index,
                             gate_source):
    debug('comedi_set_gate_source(%d, %d, %d, %d, %d)', fp, sub, channel,
          gate_index, gate_source)
    return self[fp][sub].comedi_set_gate_source(channel, gate_index, gate_source)

  def comedi_set_other_source(self, fp, sub, channel, other, source):
    debug('comedi_set_other_source(%d, %d, %d, %d, %d)', fp, sub, channel,
          other, source)
    return self[fp][sub].comedi_set_other_source(channel, other, source)

  def comedi_set_routing(self, fp, sub, channel, routing):
    debug('comedi_set_routing(%d, %d, %d, %d)', fp, sub, channel, routing)
    return self[fp][sub].set_routing(channel, routing)

  def comedi_test_route(self, fp, source, destination):
    debug('comedi_test_route(%d, %d, %d)', fp, source, destination)
    return self[fp].test_route(source, destination)

  def comedi_connect_route(self, fp, source, destination):
    debug('comedi_connect_route(%d, %d, %d)', fp, source, destination)
    return self[fp].connect_route(source, destination)

  def comedi_disconnect_route(self, fp, source, destination):
    debug('comedi_disconnect_route(%d, %d, %d)', fp, source, destination)
    return self[fp].disconnect_route(source, destination)

  def comedi_get_routes(self, fp, routelist, len_routelist):
    debug('comedi_get_routes(%d, [..], %d)', fp, len_routelist)
    return self[fp].get_routes(routelist, len_routelist)

  def comedi_get_cmd_timing_constraints(self, fp, subdevice,
                                        scan_begin_src,
                                        scan_begin_min, #ptr
                                        convert_src,
                                        convert_min,    #ptr
                                        chanlist,       #ptr
                                        chanlist_len):
    debug('comedi_get_cmd_timing_constraints(%d, %d, %d, 0x%x, %d, 0x%x, 0x%x, %d)',
          fp, subdevice,
          scan_begin_src, addressof(scan_begin_min._obj),
          convert_src, addressof(convert_min._obj),
          addressof(chanlist), chanlist_len)
    return self[fp][subdevice].get_cmd_timing_constraints(
      scan_begin_src, scan_begin_min,
      convert_src, convert_min,
      chanlist, chanlist_len
    )
