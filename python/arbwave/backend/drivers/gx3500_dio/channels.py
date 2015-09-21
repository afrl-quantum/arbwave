# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Channel definitions for the GX3500 timing/DIO board driver.

@author: bks
"""

from ...channels import Digital, Backplane
from ...channels import Timing as BaseTiming

from physical import unit
import sys

class Timing(BaseTiming):
  """
  Timing channel specialization for using the outputs as aperiodic
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
    return 50e-9 * self._divider() * unit.s

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


class PrimaryOscillator(BaseTiming):
  """
  Timing channel specialization for the possible master oscillators
  for the timing board.
  """

  def get_min_period(self):
    """
    Returns the minimum timing period (period between two rising edges of this
    clock pulse) in units of seconds.

    :return: the minimum period with physical.uinit.s
    """
    return 50e-9 * unit.s

  def get_config_template(self):
    """
    Get the config_dict template for this channel.

    :return: a dict('setting-name': {'value':v, 'type':t, 'range':xrange})
    """
    return {}
