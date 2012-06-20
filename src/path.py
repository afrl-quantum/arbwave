# vim: ts=2:sw=2:tw=80:nowrap
"""
Some tools to help manipulate the devices paths.
"""

if __name__ != '__main__':
  import backend
else:
  # for testing
  class FakeBackend:
    def __init__(self):
      self.drivers = ['ni', 'vp']
  backend = FakeBackend()


def collect_prefix(D, drop_prefixes=0, prefix_len=1, drop_path_len=0,
                   prefix_list=None):
  """
  This function serves to categorize paths by their prefix(es).
  """
  if prefix_list is None:
    prefix_list = backend.drivers
  retval = dict()
  for d in D.items():
    if d[0] is None:
      continue

    if type(d[0]) is str:
      pth = d[0].split('/')[drop_prefixes:]
      prfx = '/'.join(pth[0:prefix_len])
      pth = pth[drop_path_len:]
      key = '/'.join(pth)

    else:
      assert type(d[0]) in [list, tuple], 'collect_prefix:  key invalid: '+d[0]
      pth0 = d[0][0].split('/')[drop_prefixes:]
      pth1 = d[0][1]
      prfx = '/'.join(pth0[0:prefix_len])
      pth0 = '/'.join(pth0[drop_path_len:])

      if prfx not in prefix_list:
        # this prefix is _supposed_ to be for an existing driver
        # we resort to trying d[0][1]
        pth0 = d[0][0]
        pth1 = d[0][1].split('/')[drop_prefixes:]
        prfx = '/'.join(pth1[0:prefix_len])
        pth1 = '/'.join(pth1[drop_path_len:])

      key = (pth0, pth1)

    if prfx not in retval:
      retval[prfx] = dict()
    retval[prfx][ key ] = d[1]

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
    ('ni/Dev1/ctr0Output','TRIG/0') : {'inv': True},
    ('vp/Dev0/A/13',      'TRIG/3') : {'inv':False},
    ('TRIG/4',  'ni/Dev2/ctr0Gate') : {'inv': True},
  }

  print '\n',collect_prefix( signals, 0, 1, 1 )
  print '\n',collect_prefix( signals )
