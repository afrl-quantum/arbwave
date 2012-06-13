# vim: ts=2:sw=2:tw=80:nowrap
"""
Some tools to help manipulate the devices paths.
"""

from copy import deepcopy

if __name__ != '__main__':
  import backend
else:
  # for testing
  class FakeBackend:
    def __init__(self):
      self.drivers = ['ni', 'vp']
  backend = FakeBackend()


def collect_prefix(D, drop_prefixes=0, prefix_len=1, drop_path_len=0,
                   tryalso=None, prefix_list=None):
  """
  This function serves to categorize paths by their prefix(es).
  """
  if prefix_list is None:
    prefix_list = backend.drivers
  retval = dict()
  for d in D.items():
    if d[0] is None:
      continue

    pth = d[0].split('/')[drop_prefixes:]
    prfx = '/'.join(pth[0:prefix_len])

    if tryalso and tryalso in d[1] and prfx not in prefix_list:
      # this prefix is _supposed_ to be for an existing driver
      # we resort to trying a field within the d[1]
      pth2 = d[1][tryalso].split('/')[drop_prefixes:]
      prfx = '/'.join(pth2[0:prefix_len])
      data = deepcopy( d[1] )
      data[tryalso] = '/'.join(pth2[drop_path_len:])
    else:
      pth = pth[drop_path_len:]
      data = d[1]

    if prfx not in retval:
      retval[prfx] = dict()
    retval[prfx][ '/'.join(pth) ] = data

  return retval



if __name__ == '__main__':
  channels = {
    'label0' : {'device':'Digital/vp/Dev1/A/12'},
    'label1' : {'device':'Digital/vp/Dev1/A/13'},
    'label2' : {'device':'Digital/vp/Dev2/A/14'},
    'label3' : {'device':'Analog/ni/Dev2/ao14'},
  }

  collected = \
  collect_prefix(
    { c[1]['device']:None   for c in channels.items()},
    1 )

  print collected

  print collect_prefix( collected['vp'], 0, 2, 2 )


  signals = {
    'ni/Dev1/ctr0Output' : {'dest':'TRIG/0'},
    'vp/Dev0/A/13' : {'dest':'TRIG/3'},
    'TRIG/4'       : {'dest': 'ni/Dev2/ctr0Gate'},
  }

  print '\n',collect_prefix( signals, 0, 1, 1, tryalso='dest' )
  print '\n',collect_prefix( signals, tryalso='dest' )
