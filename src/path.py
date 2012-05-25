# vim: ts=2:sw=2:tw=80:nowrap
"""
Some tools to help manipulate the devices paths.
"""

def collect_prefix(D, drop_prefixes=0, prefix_len=1, drop_path_len=0):
  """
  This function serves to categorize paths by their prefix(es).
  """
  retval = dict()
  for d in D.items():
    if d[0] is None:
      continue

    pth = d[0].split('/')[drop_prefixes:]
    prfx = '/'.join(pth[0:prefix_len])
    if prfx not in retval:
      retval[prfx] = dict()
    retval[prfx][ '/'.join(pth[drop_path_len:]) ] = d[1]

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
