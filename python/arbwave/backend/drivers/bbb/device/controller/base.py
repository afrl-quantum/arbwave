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

  def __init__(self, hostid, type, klass):
    super(Device,self).__init__()
    self.hostid = hostid
    self.objectId = format_objectId(hostid, type)
    self.is_continuous = False

    assert bbb.version.compatible(bbb.VERSION, BBB_VERSION), \
      'AFRL/BeagleBone Black version is incompatible'

    self.device = klass()

    try:
      assert self.device.sw_fw_compatible, \
      'AFRL/BeagleBone Black software and firmware are not compatible with ' \
      'each other'
    except:
      self.close()
      raise

    self.device.reset()


  def __del__(self):
    self.close()


  def close(self):
    """
    Final cleanup.
    """
    debug('bbb.Device(%s).close()', self)
    self.device.close()


  def get_version(self):
    """return the Arbwave version"""
    return arbwave_version()


  def get_objectId(self):
    return self.objectId


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    raise RuntimeError(
      'bbb.Device({}): does not implement static output'.format(self))


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


  def start(self):
    """
    Start the sequence: arm the board.
    """
    debug('bbb.Device(%s).start()', self)
    self.device.exec_waveform(1 if not self.is_continuous else 0)


  def wait(self):
    """
    Wait for the sequence to finish.
    """
    if self.is_continuous:
      raise RuntimeError('cannot wait for continuous waveform to finish')

    reps = self.device.waitfor_waveform()
    debug('bbb.Device(%s).wait(): dds finished %d iterations', self, reps)


  def stop(self):
    """
    Forcibly stop any running sequence.  For the DDS device, this means writing
    a Null instruction to the RpMsg queue.
    """
    self.device.null_op()
    reps = self.device.waitfor_waveform()
    if reps is not None:
      # For Arbwave, this should only be executed if in continuous mode
      assert self.is_continuous, 'bbb.Device(%s): should be in continuous mode'
      debug('bbb.Device(%s).wait(): dds finished %d iterations', self, reps)
    self.is_continuous = False
