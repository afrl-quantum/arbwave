# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level comedilib library.
"""

import ctypes_comedi as c
from ctypes import c_ubyte
from logging import log, debug, info, warn, error, critical, DEBUG
import re, time
from ....tools.expand import expand_braces

def inject_sim_lib():
  C = ComediSim()
  import_funcs = [ f for f in dir(C) if f.startswith('comedi')]
  for f in import_funcs:
    setattr( c, f, getattr(C,f) )
  return C


def mk_crange(min,max,unit):
  r = c.comedi_range()
  r.min = min
  r.max = max
  r.unit = unit
  return r

class SimSubDev(dict):
  def __init__(self, *a, **kw):
    super(SimSubDev,self).__init__(*a, **kw)
    self.__dict__ = self
    # ensure that ranges are sorted correctly
    self.setdefault('type', c.COMEDI_SUBD_UNUSED)
    self.setdefault('n_channels', 0)
    # FIXME:  replace this with a non static digital/analog representation
    self.setdefault('state', [0 for i in xrange(self.n_channels)])
    self.setdefault('flags', 0)
    self.setdefault('cmd', dict())
    self.setdefault('ranges', dict())
    RI = self.ranges.items()
    self.ranges = list()
    self.buffer = (c_ubyte*self.pop('buffer_sz', 1024))(0)
    self.buf_begin = self.buf_end = 0
    self.setdefault('max_buf_size', 2**20)
    for u,r in RI:
      r = list(r)
      r.sort( key=lambda v : abs(v[0]) ) # sort ranges increasingly
      self.ranges += [ mk_crange(mn,mx,u) for mn,mx in r ]
    self.ranges = tuple( self.ranges ) # make immutable

  def find_range(self, channel, unit, min, max):
    assert min <= max, 'comedi_find_range:  min > max'
    ranges = ( r for r in self.ranges if r.unit == unit )
    for i, r in zip( xrange(len(ranges)), ranges ):
      if r.min < min and max < r.max:
        return i
    return -1

  def get_maxdata(self, channel):
    return (2<<(self.bits-1)) - 1

  def get_n_ranges(self, channel):
    return len( self.ranges ) # ignoring channel for now

  def get_range(self, channel, range):
    return self.ranges[range] if range < len(self.ranges) else None

  # AI functions
  def data_read(self, channel, range, aref, data):
    # dereference the pointer and set a value
    data._obj.value = self.state[channel]
    return 1

  def data_read_n(self, channel, range, aref, data, n):
    # dereference the pointer and set a value
    data._obj[0:n] = [self.state[channel] for i in xrange(n)]
    return n

  def data_read_delayed(self, channel, range, aref, data, nanosec):
    time.sleep( nanosec * 1e-9 )
    # dereference the pointer and set a value
    data._obj.value = self.state[channel]
    return 1

  def data_read_hint(self, channel, range, aref):
    # hint taken
    return 0

  # AO functions
  def data_write(self, channel, range, aref, data):
    self.state[channel] = data._obj.value
    return 1 # success in any case!

  # CMD functions
  def get_cmd_src_mask(self, cmd):
    for a,v in self.get('cmd',{}).items():
      setattr( cmd, a, v )
    return 0

  def set_buffer_size( self, size ):
    old = self.buffer
    self.buffer = (c_ubyte*size)( *old[:min(len(old),size)] )
    del old
    return size

  def get_buffer_contents(self):
    return self.buf_end - self.buf_begin

  def get_buffer_offset(self):
    return self.buf_begin

  def mark_buffer_read(self, num_bytes):
    if self.type not in [c.COMEDI_SUBD_AI, c.COMEDI_SUBD_DI]:
      return -1
    avail = self.get_buffer_contents()
    if num_bytes > avail:
      return -1
    self.buf_begin += num_bytes
    return num_bytes

  def mark_buffer_written(self, num_bytes):
    if self.type not in [c.COMEDI_SUBD_AO, c.COMEDI_SUBD_DO]:
      return -1
    avail = self.get_buffer_contents()
    if num_bytes > avail:
      return -1
    self.buf_begin += num_bytes
    return num_bytes

  def apply_calibration(self, channel, range, aref, file_path):
    raise NotImplementedError('not simulated yet')

  def apply_parsed_calibration(self, channel, range, aref, calib):
    raise NotImplementedError('not simulated yet')



  # Digital I/O





class SimCard(object):
  driver  = None
  board   = None
  subdevs = dict()
  def __init__(self):
    super(SimCard,self).__init__()
    # initialize subdevs...
    self.subdevs = [ SimSubDev(D) for D in self.subdevs ]

  def __getitem__(self,i):
    """Quick method of indexing the subdevice"""
    return self.subdevs[i]

  def lock(self, subdevice):
    if self.subdevs[subdevice].flags & c.SDF_LOCKED:
      return -1
    self.subdevs[subdevice].flags |= c.SDF_LOCKED | c.SDF_LOCK_OWNER
    return 0

  def unlock(self, subdevice):
    if not self.isLockedBySelf(subdevice):
      return -1
    self.subdevs[subdevice].flags &= ~(c.SDF_LOCKED | c.SDF_LOCK_OWNER)
    return 0

  def isLockedBySelf(self, subdevice):
    lock_owned = (c.SDF_LOCKED | c.SDF_LOCK_OWNER)
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

  def get_read_subdevice(self, fd):
    """
    The function comedi_get_read_subdevice() returns the index of the subdevice
    whose streaming input buffer is accessible
    through the device device . If there is no such subdevice, -1 is returned.
    """
    return self.find_subdevice_by_type(
      (c.COMEDI_SUBD_AI, c.COMEDI_SUBD_DI), 0,flagmask=c.SDF_CMD|c.SDF_CMD_READ
    )

  def get_write_subdevice(self):
    """
    The function comedi_get_write_subdevice() returns the index of the subdevice
    whose streaming output buffer is accessible through this (simulated) card. If
    there is no such subdevice, -1 is returned.
    """
    return self.find_subdevice_by_type(
      (c.COMEDI_SUBD_AO, c.COMEDI_SUBD_DO), 0,flagmask=c.SDF_CMD|c.SDF_CMD_WRITE
    )


class PXI_6733(SimCard):
  driver = 'ni_pcimio'
  board = 'pxi-6733'
  subdevs = {
    1 : dict( type=c.COMEDI_SUBD_AO, n_channels=8,
      bits=16,
      flags= c.SDF_CMD       |
             c.SDF_CMD_WRITE |
             c.SDF_DEGLITCH  |
             c.SDF_GROUND    |
             c.SDF_WRITABLE  |
             c.SDF_WRITEABLE,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=2,
               data=None,
               data_len=0,
               flags=64,
               scan_begin_arg=0,
               scan_begin_src=80,
               scan_end_arg=0,
               scan_end_src=32,
               start_arg=0,
               start_src=192,
               stop_arg=0,
               stop_src=33,
               subdev=1,
      ),
      ranges={ c.UNIT_volt : ( (-10,10), (-2,2), (-1,1) )  },
    ),
  }

def subdev_replace_n_channels(S, N):
  S[1]['n_channels'] = N
  return S
class PXI_6723(PXI_6733):
  board = 'pxi-6723'
  subdevs = subdev_replace_n_channels(PXI_6733.subdevs.copy(), 32)

class PCI_6229(SimCard):
  driver = 'ni_pcimio'
  board = 'pci-6229'
  subdevs = {
    1 : dict( type=c.COMEDI_SUBD_AO, n_channels=4,
      bits=16,
      flags= c.SDF_CMD       |
             c.SDF_CMD_WRITE |
             c.SDF_DEGLITCH  |
             c.SDF_GROUND    |
             c.SDF_WRITABLE  |
             c.SDF_WRITEABLE |
             c.SDF_SOFT_CALIBRATED,
      cmd=dict(chanlist=None,
               chanlist_len=0,
               convert_arg=0,
               convert_src=2,
               data=None,
               data_len=0,
               flags=64,
               scan_begin_arg=0,
               scan_begin_src=80,
               scan_end_arg=0,
               scan_end_src=32,
               start_arg=0,
               start_src=192,
               stop_arg=0,
               stop_src=33,
               subdev=1,
      ),
    ),
  }


class ComediSim(object):
  def __init__(self):
    self.cards = {
      0 : PXI_6733(),
      1 : PXI_6723(),
      2 : PCI_6229(),
    }

  def __getitem__(self, i):
    """Quick access to cards by index"""
    return self.cards[i]

  def glob_device_files(self):
    mn,mx = min(self.cards), max(self.cards)
    return expand_braces('/dev/comedi{{{}..{}}}'.format(mn,mx))

  def comedi_open(self, filename):
    debug('comedi_open(%s)', filename)
    m = re.match( '/dev/comedi(?P<card_number>[0-9]+)$', filename )
    if not m:
      return None

    card_number = int(m.group('card_number'))

    if card_number not in self.cards:
      return None

    # NOTE:  return the right type of value(?)
    # I think this is perfectly fine since the c-library returns a pointer to an
    # opaque type.  Hence, we can return any particular value that is convenient
    # for us.
    return card_number

  def comedi_close(self, fd):
    # FIXME:  Not sure if this implementation is any good.
    debug('comedi_close(%d)', fd)
    for d in self.cards.values():
      for sd in d.subdevs:
        if d.isLockedBySelf(sd):
          self.comedi_unlock(d,sd)
    return 0

  def comedi_fileno(self, fd):
    return fd if fd in self.cards else -1

  def comedi_get_version_code(self, fd):
    return 0x1 # we'll just return a lame version for all kernel modules

  def comedi_get_read_subdevice(self, fd):
    """
    The function comedi_get_read_subdevice() returns the index of the subdevice
    whose streaming input buffer is accessible through the (simulated) card . If
    there is no such subdevice, -1 is returned.
    """
    return self[fd].get_read_subdevice()

  def comedi_get_write_subdevice(self, fd):
    """
    The function comedi_get_write_subdevice() returns the index of the subdevice
    whose streaming output buffer is accessible through the (simulated) card. If
    there is no such subdevice, -1 is returned.
    """
    return self[fd].get_write_subdevice()

  def comedi_get_n_subdevices(self, fd):
    debug('comedi_get_n_subdevices(%d)', fd)
    return len( self[fd].subdevs )

  def comedi_get_subdevice_type(self, fd, sub):
    debug('comedi_get_subdevice_type(%d, %d)', fd, sub)
    return self[fd][sub].type

  def comedi_find_subdevice_by_type(self, fd, typ, start_subdevice):
    debug('comedi_find_subdevice_by_type(%d, %d, %d)', fd,typ,start_subdevice)
    if fd not in self.cards: return -1
    return self[fd].find_subdevice_by_type(typ, start_subdevice)

  def comedi_get_subdevice_flags(self, fd, sub):
    debug('comedi_get_subdevice_flags(%d, %d)', fd, sub)
    if fd not in self.cards: return -1
    return self[fd][sub].flags

  def comedi_get_n_channels(self, fd, sub):
    debug('comedi_get_n_channels(%d, %d)', fd, sub)
    if fd not in self.cards: return -1
    return self[fd][sub].n_channels

  def comedi_get_driver_name(self, fd):
    debug('comedi_get_driver_name(%d)', fd)
    return self[fd].driver

  def comedi_get_board_name(self, fd):
    debug('comedi_get_board_name(%d)', fd)
    return self[fd].board

  def comedi_cancel(self, fd, sub):
    debug('comedi_cancel(%d, %d)', fd, sub)
    return 0

  def comedi_lock(self, fd, sub):
    debug('comedi_lock(%d, %d)', fd, sub)
    return self[fd].lock(sub)

  def comedi_unlock(self, fd, sub):
    debug('comedi_unlock(%d, %d)', fd, sub)
    return self[fd].unlock(sub)

  def comedi_find_range(self, fd, sub, channel, unit, min, max):
    debug('comedi_find_range(%d,%d,%d,%d,%g,%g)', fd,sub,channel,unit,min,max)
    return self[fd][sub].find_range(channel, unit, min, max)

  def comedi_get_maxdata(self, fd, sub, channel):
    return self[fd][sub].get_maxdata(channel)

  def comedi_get_n_ranges(self, fd, sub, channel):
    return self[fd][sub].get_n_ranges(channel)

  def comedi_get_range(self, fd, sub, channel, range):
    return self[fd][sub].get_range(channel, range)

  def comedi_maxdata_is_chan_specific(self, fd, sub):
    #return self[fd][sub].comedi_maxdata_is_chan_specific()
    return 0

  def comedi_range_is_chan_specific(self, fd, sub):
    #return self[fd][sub].comedi_range_is_chan_specific()
    return 0


  # AI functions
  def comedi_data_read(self, fd, subdev, channel, range, aref, data):
    debug('comedi_data_read(%d, %d, %d, %d, %d, %d)',
          fd, subdev, channel, range, aref, data)
    return self[fd][subdev].data_read(channel, range, aref, data)

  def comedi_data_read_n(self, fd, subdev, channel, range, aref, data, n):
    debug('comedi_data_read_n(%d, %d, %d, %d, %d, %d, %d)',
          fd, subdev, channel, range, aref, data, n)
    return self[fd][subdev].data_read_n(channel, range, aref, data, n)

  def comedi_data_read_delayed(self, fd, subdev, channel,
                               range, aref, data, nanosec):
    """
    read single sample from channel after delaying for specified settling time
    """
    debug('comedi_data_read_delayed(%d, %d, %d, %d, %d, %d, %d)',
          fd, subdev, channel, range, aref, data, nanosec)
    return self[fd][subdev] \
      .data_read_delayed(channel, range, aref, data, nanosec)

  def comedi_data_read_hint(self, fd, subdev, channel, range, aref):
    return self[fd][subdev].data_read_hint(channel, range, aref)


  # AO functions
  def comedi_data_write(self, fd, subdev, channel, range, aref, data):
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
          fd, subdev, channel, range, aref, data)
    return self[fd][subdev].data_write(channel, range, aref, data)


  # CMD functions
  def comedi_get_cmd_src_mask(self, fd, subdev, cmd):
    debug('comedi_get_cmd_src_mask(%d, %d, %s)', fd, subdev, cmd)
    if fd not in self.cards: return -1
    return self[fd][subdev].get_cmd_src_mask(cmd)

  def comedi_internal_trigger(self, fd, subdevice, trig_num=0):
    debug('comedi_internal_trigger(%d, %d, %s)', fd, subdev, trig_num)
    return 0

  def comedi_do_insn(self, fd, instruction):
    i = instruction
    debug('comedi_do_insn(%d, %d, %s)', fd, subdev, i)
    if ( i.insn == c.INSN_WRITE ):
      C,R,A = ( f(i.chanspec) for i in [c.CR_CHAN,c.CR_RANGE,c.CR_AREF] )
      for j in xrange(i.n):
        self[fd][i.subdev].data_write(C,R,A,i.data[j])
      return i.n
    if ( i.insn == c.INSN_READ ):
      C,R,A = ( f(i.chanspec) for i in [c.CR_CHAN,c.CR_RANGE,c.CR_AREF] )
      self[fd][i.subdev].data_read_n(C,R,A,i.data,i.n)
      return i.n
    if ( i.insn == c.INSN_BITS ):
      return -1
    if ( i.insn == c.INSN_GTOD ):
      assert i.n == 2, 'INSN_GTOD requires buffer of len=2'
      t = time.time()
      i.data[0] = int(t)
      i.data[1] = int( ( t - int(t)) * 1e6 )
      return 0
    if ( i.insn == c.INSN_WAIT ):
      assert i.n == 1, 'INSN_WAIT requires buffer of len=1'
      time.sleep(i.data[0])
      return 0

    raise NotImplementedError(
      'command instruction ({}) not simulated yet'.format(i.insn))

  def comedi_do_insnlist(self, fd, instruction_list):
    debug('comedi_do_insnlist(%d, %d, %s)', fd, subdev, instruction_list)
    successes = 0
    for i in xrange(instruction_list.n_insns):
      ri = self.comedi_do_insn( instruction_list.insns[i] )
      if ri >= 0: successes += 1
      else: break
    return successes if successes > 0 else -1

  def comedi_command(self, fd, command):
    raise NotImplementedError('not simulated yet')

  def comedi_command_test(self, fd, command):
    raise NotImplementedError('not simulated yet')

  def comedi_get_buffer_contents(self, fd, subdevice):
    """
    The function comedi_get_buffer_contents() is used on a subdevice that has a
    Comedi command in progress. The number of bytes that are available in the
    streaming buffer is returned. If there is an error, -1 is returned.
    """
    debug('comedi_get_buffer_contents(%d, %d)', fd, subdevice)
    return self[fd][subdevice].get_buffer_contents()

  def comedi_get_buffer_offset(self, fd, subdevice):
    """
    The function comedi_get_buffer_offset() is used on a subdevice that has a
    Comedi command in progress. This function returns the offset in bytes of the
    read pointer in the streaming buffer.  This offset is only useful for memory
    mapped buffers. If there is an error, -1 is returned.
    """
    debug('comedi_get_buffer_offset(%d, %d)', fd, subdevice)
    return self[fd][subdevice].get_buffer_offset()

  def comedi_get_buffer_size(self, fd, subdevice):
    """
    The function comedi_get_buffer_size() returns the size (in bytes) of the
    streaming buffer for the subdevice specified by card and subdevice. On
    error, -1 is returned.
    """
    debug('comedi_get_buffer_size(%d, %d)', fd, subdevice)
    return len( self[fd][subdevice].buffer )

  def comedi_set_buffer_size(self, fd, subdevice, size):
    debug('comedi_set_buffer_size(%d, %d, %d)', fd, subdevice, size)
    self[fd][subdevice].set_buffer_size(size)

  def comedi_set_max_buffer_size(self, fd, subdevice, max_size):
    """Requires privileged execution."""
    debug('comedi_set_max_buffer_size(%d, %d, %d)', fd, subdevice, max_size)
    self[fd][subdevice].max_buf_size = max_size

  def comedi_get_max_buffer_size(self, fd, subdevice):
    debug('comedi_get_max_buffer_size(%d, %d)', fd, subdevice)
    return self[fd][subdevice].max_buf_size

  def comedi_get_cmd_generic_timed(self, fd, subdevice, command,
                                   chanlist_len, scan_period_ns):
    debug('comedi_get_cmd_generic_timed(%d, %d, %s, %d, %d)',
          fd, subdevice, command, chanlist_len, scan_period_ns)
    raise NotImplementedError('not simulated yet')

  def comedi_mark_buffer_read(self, fd, subdevice, num_bytes):
    """
    The function comedi_mark_buffer_read() is used on a subdevice that has a
    Comedi input command in progress. It should only be used if you are using a
    mmap() mapping to read data from Comedi’s buffer.
    """
    debug('comedi_mark_buffer_read(%d, %d, %d)', fd, subdevice, num_bytes)
    return self[fd][subdevice].mark_buffer_read( num_bytes )

  def comedi_mark_buffer_written(self, fd, subdevice, num_bytes):
    debug('comedi_mark_buffer_written(%d, %d, %d)', fd, subdevice, num_bytes)
    return self[fd][subdevice].mark_buffer_written( num_bytes )


  def comedi_poll(self, fd, subdevice):
    debug('comedi_poll(%d, %d)', fd, subdevice)
    # we'll just return what is available now; no actual dma
    return self[fd][subdevice].get_buffer_contents()


  # calibration
  def comedi_apply_calibration(self, fd, sub, channel, range, aref,
                               file_path):
    return self[fd][sub] \
      .apply_calibration(channel, range, aref, file_path)

  def comedi_apply_parsed_calibration(self, fd, sub, channel, range,
                                      aref, calibration):
    return self[fd][sub] \
      .apply_parsed_calibration(channel, range, aref, calibration)

  def comedi_get_default_calibration_path(self, fd):
    return self[fd].comedi_get_default_calibration_path()

  def comedi_get_hardcal_converter(self, fd, sub, channel,
                                   range, direction, converter):
    return self[fd][sub] \
      .comedi_get_hardcal_converter(channel, range, direction, converter)

  def comedi_get_softcal_converter(self, sub, channel,
                                   range, direction, parsed_calibration,
                                   converter):
    return self[fd][sub] \
      .comedi_get_softcal_converter(channel, range, direction,
                                    parsed_calibration, converter)


  # Digital I/O
  def comedi_dio_bitfield2(self, fd, sub, write_mask, bits, base_channel):
    return self[fd][sub].comedi_dio_bitfield2(write_mask, bits, base_channel)

  def comedi_dio_config(self, fd, sub, channel, direction):
    return self[fd][sub].comedi_dio_config(channel, direction)

  def comedi_dio_get_config(self, fd, sub, channel, direction):
    return self[fd][sub].comedi_dio_get_config(channel, direction)

  def comedi_dio_read(self, fd, sub, channel, bit):
    return self[fd][sub].comedi_dio_read(channel, bit)

  def comedi_dio_write(self, fd, sub, channel, bit):
    return self[fd][sub].comedi_dio_write(channel, bit)


  # Extensions
  def comedi_arm(self, fd, sub, source):
    debug('comedi_arm(%d, %d, %d)', fd, sub, source)
    # nothing to really arm...
    #return self[fd][sub].comedi_arm(source)
    return 0

  def comedi_get_clock_source(self, fd, sub, channel, clock, period_ns):
    return self[fd][sub].comedi_get_clock_source(channel, clock, period_ns)

  def comedi_get_gate_source(self, fd, sub, channel, gate_index,
                             gate_source):
    return self[fd][sub].comedi_get_gate_source(channel, gate_index, gate_source)

  def comedi_get_hardware_buffer_size(self, fd, sub, direction):
    return self[fd][sub].comedi_get_hardware_buffer_size(direction)

  def comedi_get_routing(self, fd, sub, channel, routing):
    return self[fd][sub].comedi_get_routing(channel, routing)

  def comedi_reset(self, fd, sub):
    return self[fd][sub].comedi_reset():

  def comedi_set_clock_source(self, fd, sub, channel, clock, period_ns):
    return self[fd][sub].comedi_set_clock_source(channel, clock, period_ns)

  def comedi_set_counter_mode(self, fd, sub, channel, mode):
    return self[fd][sub].comedi_set_counter_mode(channel, mode)

  def comedi_set_filter(self, fd, sub, channel, filter):
    return self[fd][sub].comedi_set_filter(channel, filter)

  def comedi_set_gate_source(self, fd, sub, channel, gate_index,
                             gate_source):
    return self[fd][sub].comedi_set_gate_source(channel, gate_index, gate_source)

  def comedi_set_other_source(self, fd, sub, channel, other, source):
    return self[fd][sub].comedi_set_other_source(channel, other, source)

  def comedi_set_routing(self, fd, sub, channel, routing):
    return self[fd][sub].comedi_set_routing(channel, routing)
