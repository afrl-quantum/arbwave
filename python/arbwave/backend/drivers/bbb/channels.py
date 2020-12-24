# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Channel definitions for the driver of the BeagleBone Black using AFRL
firmware/hardware.

No BBB outputs channels require padded timing, but rather operate on a
(timestamp, output-value) basis, similar to the viewpoint and gx3500_dio
drivers.
"""

from physical import unit
import sys

from ...channels import Analog     as ABase
from ...channels import DDS        as DDSBase
from ...channels import Digital    as DBase
from ...channels import Timing     as TBase
from ...channels import Backplane  as BBase

class Analog(ABase):
  """
  *** Analog hardware/firmware not implemented yet ***
  """

class DDS(DDSBase):
  """
  Frequency generation using the AFRL DDS cape.  This cape includes a AD9959 DDS
  chip from Analog Devices.  There are four separate output channels on this
  device.
  """
  _capabilities = {'step', 'linear'}

  def get_min_period(self):
    """
    Returns the minimum timing period in units of seconds.
    *** This needs to be measured again and corrected ***
    """
    return self.device.get_min_period()



# The minimum period is 15 clock cycles or 75ns.
# TODO: Until Arbwave may potentially gain the ability to have non-uniform
# periods for channels, it may be wise to upgrade this minimum to a more even
# value, say 100*ns
_bbb_digital_minimum_neighbor_period = 15*5*unit.ns
"""
The BeagleBone Black timing firmware _does_ have timing resolution of 5*ns, but
any two transitions must be separated by at least 75*ns..
"""

class Digital(DBase):
  """
  Digital output provided by BeagleBone Black using the AFRL PRU firmware.
  """
  _padded_timing = False

  def get_min_period(self):
    """
    Returns the minimum timing period in units of seconds.
    """
    return _bbb_digital_minimum_neighbor_period

class Timing(TBase):
  """
  Timing channel specialization for using the digital outputs as aperiodic
  clock devices.
  """
  aperiodic = True

  def __init__(self, *a, **kw):
    super(Timing,self).__init__(*a, **kw)
    self.local_name = str(self)[len(str(self.device))+1:]

  def _divider(self):
    return self.device.clocks[ self.local_name ]['divider']['value']

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.

    :return: the minimum period with physical.uinit.s
    """
    return _bbb_digital_minimum_neighbor_period * self._divider()

  def get_config_template(self):
    """
    Get the config_dict template for this channel.

    :return: a dict('setting-name': {'value':v, 'type':t, 'range':range})
    """
    return {
      'divider' : {
        'value' : 2,
        'type'  : int,
        'range' : range(2, sys.maxsize),
      }
    }

class AM335x_L3_CLK(TBase):
  """
  Timing channel specialization for the L3 peripherals of the AM335x SOC of
  which the PRUSS module is a member.  The L3 peripherals run at 200MHz with
  this being derived from the CORE_CLKOUTM4 output of the PLL block.
  """

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.

    :return: the minimum period with physical.unit.s
    """
    return 5 * unit.ns

class Backplane(BBase): pass
