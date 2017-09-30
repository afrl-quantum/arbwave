# vim: ts=2:sw=2:tw=80:nowrap

from base import Device
import dds
import timing

from controller.bbb_pyro import *

type_to_device_klass_map = {
  'dds' : dds.Device,
  'timing' : timing.Device,
}

def create_device(driver, uri, objectId):
  grp, devname, type = parse_objectId(objectId)
  assert grp == BBB_PYRO_GROUP, 'Non-bbb group found'
  return type_to_device_klass_map[type](driver, uri, devname)
