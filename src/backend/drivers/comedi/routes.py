# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

import logging
from logging import debug
from ..nidaqmx import routes as ni_routes

class NullRouteLoader(object):
  def __init__(self, device):
    debug("routes for device '%s' not yet known", device)
  def add_subdev_routes(self, subdev, typ): pass

class NIRouteLoader(object):
  def __init__(self, device):
    self.ni_rl = ni_routes.RouteLoader(device.prefix)
    self.device = device

    # route_map     (src, destination) -> (native-src, native-destination)
    # aggregate_map (src) -> [dest0, dest1, ...]
    self.aggregate_map, self.route_map = \
      self.ni_rl.mk_signal_route_map(device.device,device.board)

  def add_subdev_routes(self, subdev, typ): pass


driver_to_loader = {
  'ni_pcimio' : NIRouteLoader,
}

def getRouteLoader( driver ):
  return driver_to_loader.get(driver, NullRouteLoader)
