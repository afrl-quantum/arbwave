import random, sys, logging
from logging import log, debug, info, warn, error, critical, DEBUG
import viewpoint as vp
from ctypes import cast, POINTER

class DIO64:
  def __init__(self):
    self.attributes = dict()
    self.out_len_mask = 0

  def DIO64_Open( self, board, ignored ):
    debug('DIO64_Open(%d,%s)', board, ignored)

  def DIO64_Load( self, board, rbfFile, num_inputs, num_outputs ):
    debug('DIO64_Load(%d,%s,%s,%s)', board, repr(rbfFile), num_inputs, num_outputs)

  def DIO64_Close( self, board ):
    debug('DIO64_Close(%d)', board)

  def DIO64_In_Start( self, board, ticks, mask, len_mask, ignored_flags, clock,
                      trig_type_edge, trig_source,
                      stop_type_edge, stop_source,
                      daq_clock_modulo, scan_rate ):
    debug('DIO64_In_Start(%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
          board, ticks, mask, len_mask, ignored_flags, clock,
          trig_type_edge, trig_source, stop_type_edge, stop_source,
          daq_clock_modulo, scan_rate )

  def DIO64_In_Status( self, board, scans_avail_out, status_out ):
    scans_avail_out._obj.value = 0
    debug('DIO64_In_Status(%d,%s,%s)', board, scans_avail_out, status_out )

  def DIO64_In_Read( self, board, buffer_out, scansToRead, status_in_out ):
    debug('DIO64_In_Read( %d,%s,%s,%s)',
          board, buffer_out, scansToRead, status_in_out )

  def DIO64_In_Stop( self, board ):
    debug('DIO64_In_Stop(%d)', board )

  def DIO64_Out_ForceOutput( self, board, buf, mask ):
    buf_len = 0
    while (mask >> buf_len): buf_len += 1
    log(DEBUG-1, 'DIO64_Out_ForceOutput(%d): %s', board, buf[0:buf_len])

  def DIO64_Out_GetInput( self, board, buf ):
    debug('DIO64_Out_GetInput(%d,%s)', board, buf )

  def DIO64_Out_Config( self, board, ticks, mask, len_mask, ignored_flags, clock,
                        trig_type_edge, trig_source,
                        stop_type_edge, stop_source,
                        daq_clock_modulo, repetitions,
                        number_transitions, scan_rate ):
    self.out_len_mask = len_mask
    debug('DIO64_Out_Config(%d,%d,%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
          board, ticks, mask[:], len_mask, ignored_flags, clock,
          trig_type_edge, trig_source, stop_type_edge, stop_source,
          daq_clock_modulo, repetitions, number_transitions, scan_rate )

  def DIO64_Out_Start( self, board ):
    debug('DIO64_Out_Start(%d)', board)

  def DIO64_Out_Status( self, board, scans_avail_out, status_out ):
    # we'll pretend to be _really_ generous
    scans_avail_out._obj.value = sys.maxint
    status_out._obj.time.value = sys.maxint
    debug('DIO64_Out_Status(%d,%s,%s)', board, scans_avail_out, status_out )

  def DIO64_Out_Write( self, board, buf, buf_len, status_in_out ):
    debug('DIO64_Out_Write(%d,%s,%d,%s)', board, buf, buf_len, status_in_out)

  def DIO64_Out_Stop( self, board ):
    debug('DIO64_Out_Stop(%d)', board )

  def DIO64_SetAttr( self, board, attrId, value ):
    debug('DIO64_SetAttr(%d, %d, %d)', board, attrId, value)
    self.attributes[attrId] = value

  def DIO64_GetAttr( self, board, attrId, value_out ):
    aid = attrId._obj.value
    debug('DIO64_GetAttr(%d, %s(%d), %s)', board, attrId, aid, value_out)

    if aid in self.attributes:
      return self.attributes[aid]

    valid_vals = vp.attributes.values[aid][0]
    if valid_vals is None:
      v_type = vp.attributes.values[aid][1]
      if v_type is int:
        retval = random.randint(0, sys.maxint)
      elif v_type is float:
        retval = random.random()
      else:
        retval = v_type( random.randint(0, sys.maxint) )
    else:
      retval = random.sample( valid_vals, 1 )

    value_out._obj.value = retval
    self.attributes[aid] = retval
