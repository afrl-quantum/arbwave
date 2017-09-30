#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""

import sys
from os.path import join as path_join, dirname, pardir
sys.path.insert(0, path_join( dirname(__file__), *((pardir,)*5) ) )


import bbb
from logging import debug

from version import version as arbwave_version
from bbb_pyro import format_objectId

BBB_VERSION = 'bbb-0.0.1'



class Device(object):
  """
  The Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid, type):
    super(Device,self).__init__()
    self.hostid = hostid
    self.objectId = format_objectId(hostid, type)

    assert bbb.version.compatible(bbb.VERSION, BBB_VERSION), \
      'AFRL/BeagleBone Black version is incompatible'

  def __repr__(self):
    return self.objectId

  def assert_sw_fw_compatibility(self):
    try:
      assert self.sw_fw_compatible, \
      'AFRL/BeagleBone Black software and firmware are not compatible with ' \
      'each other'
    except:
      self.close()
      raise


  def __del__(self):
    self.close()


  def get_version(self):
    """return the Arbwave version"""
    return arbwave_version()


  def get_objectId(self):
    return self.objectId


  def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
    """
    Set the output waveforms for the AFRL/BeagleBone Black device.

    :param waveforms:
      a dict('channel': {<wfe-path>: (<encoding>, [(t1, val1), (t2, val2)])})
                      (see gui/plotter/digital.py for format)
                      where wfe-path means waveform element path, referring to
                      the unique identifier of the specific waveform element a
                      particular set of values refers to.
    :param clock_transitions: a dict('channel': { 'dt': dt, 
                              'transitions': iterable})
                              (see processor/engine/compute.py for format)
    :param t_max: the maximum duration of any channel
    :param continuous: bool of continuous or single-shot mode
    """
    raise RuntimeError(
      'bbb.Device({}): does not implement waveforms'.format(self))
