#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""

from ......version import version as arbwave_version
from ...device import format_objectId


class Device(object):
  """
  The Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid, type):
    super(Device,self).__init__()
    self.hostid = hostid
    self.objectId = format_objectId(hostid, type)


  def __del__(self):
    self.close()


  def close(self):
    pass


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
    raise RuntimeError(
      'bbb.Device({}): does not implement waveforms'.format(self))


  def wait(self):
    """
    Wait for the sequence to finish.
    """
    raise RuntimeError(
      'bbb.Device({}): does not implement waveforms'.format(self))


  def stop(self):
    """
    Forcibly stop any running sequence.  For the DDS device, this means writing
    a Null instruction to the RpMsg queue.
    """
    raise RuntimeError(
      'bbb.Device({}): does not implement waveforms'.format(self))
