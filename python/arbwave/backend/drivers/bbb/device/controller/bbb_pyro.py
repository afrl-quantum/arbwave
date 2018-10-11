# vim: ts=2:sw=2:tw=80:nowrap

BBB_PYRO_GROUP = 'bbb'
DDS_PYRO4_PORT = 1401
TIMING_PYRO4_PORT = 1402

def format_objectId(hostid, type):
  return '{}.{}/{}'.format(BBB_PYRO_GROUP, hostid, type)

def parse_objectId(objectId):
  grp, _, devname = objectId.partition('.')
  _, _, type = devname.partition('/')
  return grp, devname, type
