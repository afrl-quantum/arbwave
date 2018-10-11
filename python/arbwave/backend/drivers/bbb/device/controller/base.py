#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""

import sys
from os.path import join as path_join, dirname, pardir

import Pyro4

import bbb
from logging import debug

from ......version import version as arbwave_version
from .bbb_pyro import format_objectId

BBB_VERSION = 'bbb-0.2.0'



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

  @Pyro4.expose
  def get_version(self):
    """return the Arbwave version"""
    return arbwave_version()

  @Pyro4.expose
  def get_objectId(self):
    return self.objectId
