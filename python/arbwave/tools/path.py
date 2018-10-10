# vim: ts=2:sw=2:tw=80:nowrap
"""
Some tools to help manipulate the devices paths.
"""

if __name__ == '__main__':
  # for testing
  class FakeBackend:
    def __init__(self):
      self.all_drivers = ['ni', 'vp']
  backend = FakeBackend()


def collect_prefix(D, drop_prefixes=0, prefix_len=1, drop_path_len=0,
                   prefix_list=None):
  """
  This function serves to categorize paths by their prefix(es).
  """
  if prefix_list is None:
    #need postponed loading to allow backends to import this
    if __name__ != '__main__':
      from .. import backend
    else:
      global backend
    prefix_list = backend.all_drivers
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
    'label0' : {'device':'vp/Dev1/A/12'},
    'label1' : {'device':'vp/Dev1/A/13'},
    'label2' : {'device':'vp/Dev2/A/14'},
    'label3' : {'device':'ni/Dev2/ao14'},
  }
  ans1 = {
    'vp': {'vp/Dev1/A/12': None, 'vp/Dev1/A/13': None, 'vp/Dev2/A/14': None},
    'ni': {'ni/Dev2/ao14': None},
  }
  ans2 = {'vp/Dev1': {'A/12': None, 'A/13': None}, 'vp/Dev2': {'A/14': None}}

  collected = \
  collect_prefix({ c[1]['device']:None   for c in channels.items()})

  print('collect-channels-:\n', collected)
  print(' Should be:\n', ans1, '\n')

  print('collect-channels-vp:\n', collect_prefix( collected['vp'], 0, 2, 2 ))
  print(' Should be:\n', ans2, '\n')


  signals = {
    ('ni/Dev1/ctr0Output','TRIG/0') : {'inv': True},
    ('vp/Dev0/A/13',      'TRIG/3') : {'inv':False},
    ('TRIG/4',  'ni/Dev2/ctr0Gate') : {'inv': True},
  }
  ans3 = {
    'ni': {
      ('Dev1/ctr0Output', 'TRIG/0'): {'inv': True},
      ('TRIG/4', 'Dev2/ctr0Gate'): {'inv': True},
    },
    'vp': {('Dev0/A/13', 'TRIG/3'): {'inv': False}},
  }
  ans4 = {
    'ni': {
      ('ni/Dev1/ctr0Output', 'TRIG/0'): {'inv': True},
      ('TRIG/4', 'ni/Dev2/ctr0Gate'): {'inv': True},
    },
    'vp': {('vp/Dev0/A/13', 'TRIG/3'): {'inv': False}},
  }
  ans5 = {'vp/Dev0': {'A/15': None, 'A/14': None}, 'vp/Dev1': {'A/0': None}}

  print('collect-signals-0:\n', collect_prefix( signals, 0, 1, 1 ))
  print(' Should be:\n', ans3, '\n')
  print('collect-signals-1:\n', collect_prefix( signals ))
  print(' Should be:\n', ans4, '\n')


  clocks = set(['vp/Dev0/A/15', 'vp/Dev0/A/14', 'vp/Dev1/A/0'])
  print('collect-clocks:\n', collect_prefix( dict.fromkeys(clocks), 0, 2, 2 ))
  print(' Should be:\n', ans5, '\n')
