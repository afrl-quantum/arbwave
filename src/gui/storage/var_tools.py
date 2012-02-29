# vim: ts=2:sw=2:tw=80:nowrap

import copy
import pprint

def writevars( F, vardict ):
  if not F:
    return
  for i in vardict.items():
    F.write( '{K} = \\\n'.format(K=str(i[0])) )
    pprint.pprint(i[1], F )
    F.write('\n')

def readvars( F ):
  if not F:
    return None
  exec(F)
  retval = copy.copy( locals() )
  retval.pop('F')
  return retval
