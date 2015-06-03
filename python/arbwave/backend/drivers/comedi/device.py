# vim: ts=2:sw=2:tw=80:nowrap

import logging, re
from logging import log, debug, DEBUG
import ctypes_comedi as c

from ....tools import cached
import subdevice
import channels
from . import routes

def subdev_iterator(fd, typ):
  i = 0
  while True:
    i = c.comedi_find_subdevice_by_type(fd, typ, i)
    if i < 0: break
    yield i
    i += 1

klasses = {
  c.COMEDI_SUBD_AO      : subdevice.Analog,
  c.COMEDI_SUBD_DO      : subdevice.Digital,
  c.COMEDI_SUBD_DIO     : subdevice.Digital,
  c.COMEDI_SUBD_COUNTER : subdevice.Timing,
}

def get_useful_subdevices(route_loader, device, typ,
                          restrictions=dict(
                            start_src=c.TRIG_FOLLOW|c.TRIG_INT|c.TRIG_EXT,
                          ),
                         ):
  L = list()
  cmd = c.comedi_cmd_struct()

  klass = klasses[typ]
  for index in subdev_iterator(device.fd, typ):
    if c.comedi_get_cmd_src_mask(device.fd, index, cmd) < 0:
      # we only will look at those subdevs that can have asynchronous use
      log(DEBUG-1, 'ignoring subdev without async mode: %s/%d', device, index)
      continue
    if not reduce( lambda x,y: x|y,
                   [ getattr(cmd,n) & r for n,r in restrictions.items() ]):
      # we only return unrestricted devs
      debug( 'ignoring restricted subdev: %s/%s(%d)',
             device, klass.subdev_type, index )
      if logging.root.getEffectiveLevel() <= (DEBUG-1):
        log(DEBUG-1, 'cmd restrictions: %s', restrictions)
        log(DEBUG-1, 'cmd capabilities: %s',
                     { n:getattr(cmd,n) for n in restrictions })
      continue
    L.append( (device, index) )
  #del cmd # Syntax error to delete this!?!
  subdevs = list()
  for li in L:
    try: subdevs.append(klass( route_loader, name_uses_subdev=(len(L)>1), *li))
    except: pass
  return subdevs

class Device(object):
  @staticmethod
  def parse_dev(dev):
    m = re.match('/dev/comedi(?P<device>[0-9]+)$', dev)
    return None if not m else m.group('device')

  def __init__(self, prefix, device):
    self.prefix = prefix
    self.dev    = device
    self.fd     = c.comedi_open(self.dev)
    if self.fd is None:
      raise NameError('could not open comedi device: ' + self.dev)
    self.device = 'Dev'+self.parse_dev(device)
    rl = routes.getRouteLoader(self.driver) ( self )
    gus = get_useful_subdevices
    self.ao_subdevices      = gus(rl, self, c.COMEDI_SUBD_AO)
    self.do_subdevices      = gus(rl, self, c.COMEDI_SUBD_DO)
    self.dio_subdevices     = gus(rl, self, c.COMEDI_SUBD_DIO)
    self.counter_subdevices = gus(rl, self, c.COMEDI_SUBD_COUNTER)

    self.subdevices       = { str(ao):ao for ao in self.ao_subdevices }
    self.subdevices.update( { str(do):do for do in self.do_subdevices } )
    self.subdevices.update( { str(co):co for co in self.counter_subdevices } )

    self.signals = [
      channels.Backplane(src,destinations=dest,invertible=True)
      for src,dest in rl.aggregate_map.iteritems()
    ]

    #self.backplane_subdevice = None
    #if self.driver.startswith('ni_'):
    #  FIXME:  we should not need to use ni_ specifically here.  that should be
    #  taken care of in RouteLoader
    #  # for now, we only know how to deal with NI devices (that have the
    #  # backplane on subdevice 10)
    #  self.backplane_subdevice = subdevice.Backplane(self.fd,10,self.prefix)
    # *** actually, as Ian has found, subdevice=7 is also special as it
    # represents the PFI I/O lines.

  def __str__(self):
    return '{}/{}'.format(self.prefix, self.device)

  def __del__(self):
    # first instruct each one of the subdevs to be deleted
    # the intent is that this will (for each subdevice):
    #   - cancel all running jobs ( comedi_cancel )
    while self.subdevices:
      subname, subdev = self.subdevices.popitem()
      del subdev

    # Set all routes to their default and configure all routable pins to
    # COMEDI_INPUT as an attempt to protect any pins from damage
    # Following Ian's work, this means using both "Backplane" type subdevices (7
    # and 10) to unroute and protect all RTSI/PXI trigger lines and all PFI I/O
    # lines.
    # FIXME:  properly close/delete all "Signal" subdevices (like PFI and RTSI)

    # now close the device
    c.comedi_close(self.fd)

  @cached.property
  def board(self):
    return c.comedi_get_board_name(self.fd).lower()

  @cached.property
  def driver(self):
    return c.comedi_get_driver_name(self.fd).lower()
