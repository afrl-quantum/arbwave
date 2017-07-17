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
  _padded_timing = False

class DDS(DDSBase):
  """
  Frequency generation using the AFRL DDS cape.  This cape includes a AD9959 DDS
  chip from Analog Devices.  There are four separate output channels on this
  device.
  """
  _padded_timing = False
  _capabilities = {'step', 'linear'}

  def get_min_period(self):
    """
    Returns the minimum timing period in units of seconds.
    *** This needs to be measured again and corrected ***
    """
    return 1*unit.us



_bbb_digital_minimum_neighbor_period = 45*unit.ns
"""
The BeagleBone Black timing firmware _does_ have timing resolution of 5*ns, but
any two transitions must be separated by at least 45*ns.  We may want to limit
this to 50*ns instead of 45*ns to be consistent with the timing provided by
viewpoint and gxt.
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

  def _divider(self):
    return self.device.clocks[ str(self) ]['divider']['value']

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

    :return: a dict('setting-name': {'value':v, 'type':t, 'range':xrange})
    """
    return {
      'divider' : {
        'value' : 2,
        'type'  : int,
        'range' : xrange(2, sys.maxint),
      }
    }


class Backplane(BBase): pass