# vim: ts=2:sw=2:tw=80:nowrap
"""
Some tools to help enumerate subdevices.
"""

import logging
from logging import log, debug, DEBUG
import comedi

from .analog  import Analog
from .digital import Digital
from .timing  import Timing


def subdev_iterator(fp, typ):
  i = 0
  while True:
    i = comedi.find_subdevice_by_type(fp, typ, i)
    if i < 0: break
    yield i
    i += 1


klasses = {
  comedi.SUBD_AO      : Analog,
  comedi.SUBD_DO      : Digital,
  comedi.SUBD_DIO     : Digital,
  comedi.SUBD_COUNTER : Timing,
}


def get_useful_subdev_list(card, typ,
    restrictions=dict(start_src=comedi.TRIG_FOLLOW
                               |comedi.TRIG_INT
                               |comedi.TRIG_EXT),
  ):
  klass = klasses[typ]

  L = list()
  cmd = comedi.cmd()
  for index in subdev_iterator(card, typ):
    if comedi.get_cmd_src_mask(card, index, cmd) < 0:
      # we only will look at those subdevs that can have asynchronous use
      log(DEBUG-1, 'ignoring subdev without async mode: %s/%d', card, index)
      continue
    if not reduce( lambda x,y: x|y,
                   [ getattr(cmd,n) & r for n,r in restrictions.items() ]):
      # we only return unrestricted devs
      debug( 'ignoring restricted subdev: %s/%s(%d)',
             card, klass.subdev_type, index )
      if logging.root.getEffectiveLevel() <= (DEBUG-1):
        log(DEBUG-1, 'cmd restrictions: %s', restrictions)
        log(DEBUG-1, 'cmd capabilities: %s',
                     { n:getattr(cmd,n) for n in restrictions })
      continue
    L.append( (card, index) )
  return L



def get_useful_subdevices(card, typ, ret_index_list=False, **kwargs):
  klass = klasses[typ]
  L = get_useful_subdev_list(card, typ, **kwargs)

  nus = len(L) > 1

  subdevs = list()
  for li in L:
    try: subdevs.append(klass( card.route_loader, name_uses_subdev=nus, *li))
    except: pass
  if ret_index_list: #added to collect subdev number
    return L
  else:
    return subdevs
