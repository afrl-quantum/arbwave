# vim: ts=2:sw=2:tw=80:nowrap

from logging import log, debug, info, warn, error, critical, DEBUG
import re
from ctypes import c_uint, sizeof
from itertools import izip
from .. import ctypes_comedi as clib

from .....tools.float_range import float_range
from .subdevice import Subdevice as Base

class Digital(Base):
  subdev_type = 'do'

  default_range_min   = 0
  default_range_max   = 1
  reference_value     = clib.AREF_GROUND

  # FIXME:  create another device interface class that implements most of the
  # DOTiming clocks stuff that this _and_ NI implement.  Then, inherit from that
  # so that we don't have to implement it twice.


  def config_all_channels(self):
    """
    For digital channels, we must first configure the IO pins to be for OUTPUT.
    Furthermore, we need to ensure that DOTiming channels are also included.
    """
    channels = self.channels.copy()
    if self.clocks:
      # add DOTiming clock channels
      lc = len(self.channels)
      channels.update( (clk,dict(order=lc)) for clk in self.clocks )

    for chname in channels:
      ch = self.get_channel( chname )
      clib.comedi_dio_config(self.card, self.subdevice, ch, clib.COMEDI_OUTPUT)

    return self._config_all_channels( channels )


  def set_output(self, data):
    # this specialization is probably not so necessary since the standard
    # subdevice.set_output will probably also work
    bits = c_uint(0)

    if self.clocks:
      data = data.copy()
      # we just set all DOTiming clock lines to zero for static output
      data.update( { clk:0 for clk in self.clocks } )

    if (8*sizeof(bits)) < max( len(data), len(self.channels) ):
      # I don't believe this should ever be the case, but just in case, we'll
      # use the more generic insnslist based version in subdevice.set_output
      super(Digital,self).set_output(data)

    write_mask = 0
    for chname, value in data.items():
      ch = self.get_channel( chname )
      bits.value |= bool(value) << ch
      write_mask |= 1 << ch

    clib.comedi_dio_bitfield2(
      self.card,
      self.subdevice,
      write_mask,
      byref(bits),
      base_channel=0,
    )
    return bits.value


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set up the hardware for waveform output.  This function does:
      1.  Sets sample clock properly.
      2.  Sets triggering.
      3.  Writes data to hardware buffers without auto_start.

      waveforms : see gui/plotter/digital.py for format
      clock_transitions :  dictionary of clocks to dict(ignore,transitions)
      t_max : maximum time of waveforms
    """
    if set(waveforms.keys()).intersection( clock_transitions.keys() ):
      raise RuntimeError('NI channels cannot be used as clocks and ' \
                         'output simultaneously')
    if self.clocks:
      # add data for all DOTiming clock lines

      my_dt_clk = clock_transitions[ self.config['clock']['value'] ]['dt']
      waveforms = waveforms.copy()

      for clk, clkcfg in self.clocks.items():
        this_clock = clock_transitions[clk]
        dt_scale = clkcfg['divider']['value']

        # !!!! THIS CHOICE IS NOT ARBITRARY !!!!
        # This choice is our standard in arbwave.  We require this to be the
        # same as is used in
        # processor.engine.compute._insert_into_parent_clock_transitions
        dt_on = int( dt_scale / 2 )

        transitions = np.array( list( this_clock['transitions'] ), dtype=int )
        transitions.sort()

        Tlist = [((ti, True), (ti+dt_on, False)) for ti in transitions*dt_scale]
        waveforms[clk] =  { (-1,): list(chain(*Tlist)) }

    super(Digital,self) \
      .set_waveforms( waveforms, clock_transitions, t_max, continuous)


  def set_clocks(self, clocks):
    """
    Aperiodic clock implemented by a digital line of a digital device.
    """
    if self.clocks != clocks:
      self.clocks = clocks
