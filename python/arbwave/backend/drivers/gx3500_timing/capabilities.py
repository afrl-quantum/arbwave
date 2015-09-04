# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Capabilities generator for the GX3500 timing card. Piggybacks on a bunch
of the Viewpoint DIO64 driver code.

FIXME: This is a bit of a hack.

@author: bks
"""

from ..viewpoint import channels

def get_channels(devices, C, *args, **kwargs):
  """
  Construct the channel list for each device. Each device has 4 ports,
  32 bits per channel grouped into segments of 4 bits each. Each segment
  is one CAT-5e cable.
  
  :param devices: the devices map
  :param C: the chanel type to construct
  :return: a list of channels of type C
  """
  retval = list()
  for dev in devices.values():
    nin = 0
    for port in 'ABCD':
      for group in 'EFGHJKLM':
        for line in xrange(4):
          retval.append(
            C('{}/{}/{}{}'.format(dev, port, group, line), dev=dev, *args, **kwargs)
          )
  return retval

def get_digital_channels(devices):
  """
  Get the set of digital channels for all the devices.
  
  :param devices: the devices map
  :return: a list of Digital channels
  """
  return get_channels(devices, channels.Digital, explicit_timing=False)

def get_timing_channels(devices):
  """
  Get the set of timing channels for all the devices. This is both the the
  output ports and the base oscillators which ultimately clock them.
  
  :param devices: the devices map
  :return: a list of Timing channels
  """
  tlist = get_channels(devices, channels.Timing)
  # now add the internal clock(s)
  for dev in devices.values():
    tlist += [
      channels.InternalTiming('{}/Internal_XO'.format(dev), dev=dev),
      channels.InternalTiming('{}/Internal_PXI_10_MHz'.format(dev), dev=dev),
    ]
  return tlist

def get_routeable_backplane_signals(devices):
  """
  Get the set of signals which can be routed, either externally or
  onto the PXI triggers.
  
  :param devices: the devices map
  :return: a list of Backplane channels
  """
  def H(fmt, *args):
      return fmt.format(*args)

  # use get_channels() to create a template list
  template = get_channels( devices, channels.Backplane,
                           destinations=['External/'], invertible=False )

  def add_destinations(chan):
    host = chan.dev.driver.host_prefix
    destinations = ['External/'] + [H('{}TRIG/{}', host, n) for n in xrange(8)]
    return channels.Backplane(chan.name, destinations=destinations, invertible=False)

  return [add_destinations(chan) for chan in template]
