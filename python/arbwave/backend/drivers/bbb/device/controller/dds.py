#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Remote device interface for the BeagleBone Black using AFRL firmware/hardware.
"""


if __name__ == '__main__':
  import sys, argparse, socket
  from os.path import join as path_join, dirname, pardir
  sys.path.insert(0, path_join( dirname(__file__), *((pardir,)*5) ) )
  import arbwave.drivers.bbb.device.controller.dds as dds

  hostname = socket.gethostname()
  parser = argparse.ArgumentParser()
  parser.add_argument('--hostid', default=hostname,
    help='Specify the hostid label for this BeagleBone Black [Default: {}]'
         .format(hostname))
  args = parser.parse_args()

  dds.main(args.hostid)
  sys.exit()

def main(hostid):
  import Pyro.core, Pyro.naming
  Pyro.core.initServer()

  # locate the NS
  daemon = Pyro.core.Daemon()
  try:
    locator = Pyro.naming.NameServerLocator()
    print 'searching for Naming Service...'
    ns = locator.getNS()
  except NamingError:
    ns = None

  if ns is not None:
    print 'Could not find name server'
    daemon.useNameServer(ns)

    # make sure our namespace group exists
    try: ns.createGroup(BBB_PYRO_GROUP)
    except NamingError: pass

  obj = Pyro.core.ObjBase()
  device = dds.Device(hostid)
  obj.delegateTo(device)
  uri = daemon.connect(obj, device.objectId)
  print 'my uri is: ', uri

  try:
    daemon.requestLoop()
  except:
    # try removing self from Pyro name server
    try: ns.unregister(device.objectId)
    except NamingError: pass




import copy
import itertools
from logging import debug
import numpy as np
from physical import units
import time

import bbb

from .....tools import cached
from ....device import BBB_PYRO_GROUP, format_objectId
from .. import channels
from .base import Device as Base


BBB_VERSION = 'bbb-0.1.0'


class Device(Base):
  """
  The Logical Device for a single instance of the BeagleBone Black using AFRL
  firmware/hardware.
  """

  def __init__(self, hostid):
    super(Device,self).__init__(hostid, 'dds')

    self.config = self.get_config_template()
    self.is_continuous = False
    self.set_output({}) # write the port values to the hardware

    assert bbb.version.compatible(bbb.VERSION, BBB_VERSION), \
      'AFRL/BeagleBone Black version is incompatible'

    self.device = bbb.ad9959.Device()

    try:
      assert self.device.sw_fw_compatible, \
      'AFRL/BeagleBone Black software and firmware are not compatible with ' \
      'each other'
    except:
      self.close()
      raise

    # after this reset, the system clock will have to be setup
    self.device.reset()


  def close(self):
    """
    Final cleanup.
    """
    debug('bbb.Device(%s).close()', self)
    self.device.close()


  def set_sysclk(self, refclk, sysclk, charge_pump, has_crystal_refclk):
    refclk_MHz = refclk / 1e6 # must be in MHz
    sysclk_MHz = sysclk / 1e6 # must be in MHz
    charge_pump = bbb.ad9959.regs.FR1.CHARGE_PUMP['_'+charge_pump]
    self.device.set_sysclk(refclk,_MHz sysclk_MHz, charge_pump,
                           has_crystal_refclk)


  def get_sysclk(self):
    D = self.device.get_sysclk()
    D.sysclk = D.pop('sysclk_MHz') * 1e6
    D.refclk = D.pop('refclk_MHz') * 1e6
    # convert the charge_pump value into a nice string representation, but drop
    # the '_' prefix
    D.charge_pump = bbb.ad9959.regs.FR1.CHARGE_PUMP.reverse()[D.charge_pump][1:]
    # convert this to standard dict to more easily get across Pyro boundaries
    return dict(D)


  def get_charge_pump_values(self):
    """
    Return a list of string representations for all possible PLL charge pump
    values.
    """
    # remove the '_'_ prefix
    return tuple(v[1:] for v in bbb.ad9959.regs.FR1.CHARGE_PUMP.iterkeys())


  def set_output(self, values):
    """
    Immediately force the output on several channels; all others are
    unchanged.

    :param values: the channels to set. May be a dict of { <channel>: <value>},
                   or a list of [ (<channel>, <value>), ...] tuples or something
                   equivalently coercable to a dict
    """
    debug('bbb.Device(%s).set_output(values=%s)', self, values)
    if not isinstance(values, dict):
      values = dict(values)

    ch_shift = dict(ch0=0, ch1=1, ch2=2, ch3=3)
    for channel, val in values.iteritems():
      self.device.set_frequency(val, ch_shift(channel))


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
    debug('bbb.Device(%s).set_waveforms(waveforms=%s, clock_transitions=%s, ' \
          't_max=%s, continuous=%s)',
          self, waveforms, clock_transitions, t_max, continuous)
    if self.connection:
      #self.connection.set_waveforms(
      #  waveforms, clock_transitions, t_max, continuous)
      pass
    self.is_continuous = continuous


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
