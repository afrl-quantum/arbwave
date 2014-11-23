# vim: ts=2:sw=2:tw=80:nowrap

import logging
from logging import log, debug, DEBUG
import comedi as c

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

def get_useful_subdevices(route_loader, device, typ, prefix,
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
      continue
    if not reduce( lambda x,y: x|y, [
             getattr(cmd,ri) & (c.TRIG_FOLLOW|c.TRIG_INT|c.TRIG_EXT)
             for n, r in restrictions.items() ]):
      # we only return unrestricted devs
      continue
    route_loader.add_subdev_routes( index, typ )
    L.append( (device, index) )
  del cmd
  return [ klass( name_uses_subdev=(len(L)>1), *li) for li in L ]

class Device(object):
  def __init__(self, rl, prefix, device):
    self.prefix = prefix
    self.device = device
    self.fd     = c.comedi_open(self.device)
    rl = routes.getRouteLoader(self.driver) ( self )
    gus = get_useful_subdevices
    self.ao_subdevices      = gus(rl, self, c.COMEDI_SUBD_AO)
    self.do_subdevices      = gus(rl, self, c.COMEDI_SUBD_DO)
    self.dio_subdevices     = gus(rl, slef, c.COMEDI_SUBD_DIO)
    self.counter_subdevices = gus(rl, self, c.COMEDI_SUBD_COUNTER)

    self.subdevices       = { str(ao):ao for ao in self.ao_subdevices }
    self.subdevices.update( { str(do):do for do in self.do_subdevices } )
    self.subdevices.update( { str(co):co for co in self.counter_subdevices } )

    log(DEBUG-1,          
      'creating NIDAQmx backplane channel: (%s --> %s)',
      rl.aggregate_map.iteritems()
    )
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

  def __str__(self):
    return '{}/{}'.format(self.prefix, self.device)

  def __del__(self):
    # first instruct each one of the subdevs to be deleted
    while self.subdevices:
      subname, subdev = self.subdevices.popitem()
      del subdev
    # now close the device
    c.comedi_close(self.fd)

  @cached.property
  def board(self):
    return c.comedi_get_board_name(self.fd).lower()

  @cached.property
  def driver(self):
    return c.comedi_get_driver_name(self.fd).lower()
