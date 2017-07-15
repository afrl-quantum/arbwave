# vim: ts=2:sw=2:tw=80:nowrap

from base import Device
import dds
#import timing

BBB_PYRO_GROUP = ':bbb'

type_to_device_klass_map = {
  'dds' : dds.Device,
#  'timing' : Timing,
}

def format_objectId(hostid, type):
  return '{}.{}/{}'.format(BBB_PYRO_GROUP, hostid, type)

def parse_objectId(objectId):
  grp, _, devname = objectId.partition('.')
  _, _, type = devname.partition('/')
  return grp, devname, type

def create_device(driver, uri, objectId):
  grp, devname, type = parse_objectId(objectId)
  assert grp == BBB_PYRO_GROUP, 'Non-bbb group found'
  return type_to_device_klass_map[type](driver, uri, devname)
