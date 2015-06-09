# vim: ts=2:sw=2:tw=80:nowrap
"""
  The set of routes that are possible depending on the particular hardware.
"""

import logging, re
from logging import debug
from ..nidaqmx import routes as ni_routes

class BaseRouteLoader(object):
  """
  specializations should create *first before calling this*:
  route_map     (src, destination) -> (native-src, native-destination)
  aggregate_map (src) -> [dest0, dest1, ...]
  """
  def __init__(self, device, aggregate_map, route_map):
    self.device         = device
    self.aggregate_map  = aggregate_map
    self.route_map      = route_map
    self.source_map     = dict()
    for src,dst in route_map:
      D = self.source_map.setdefault( dst, list() )
      D.append(src)

class NullRouteLoader(BaseRouteLoader):
  def __init__(self, device):
    debug("routes for device '%s' not yet known", device)



class NIRouteLoader(BaseRouteLoader):
  def __init__(self, driver, device ):
    ni_rl = ni_routes.RouteLoader( driver.host_prefix, str(driver) )
    aggregate_map, route_map = \
      ni_rl.mk_signal_route_map(device.device,device.board)
    super(NIRouteLoader,self).__init__(device, aggregate_map, route_map)
    self.ni_rl = ni_rl
  
  
  

kernel_module_to_loader = {
  'ni_pcimio' : NIRouteLoader,
}

def getRouteLoader( kernel_module ):
  return kernel_module_to_loader.get(kernel_module, NullRouteLoader)
