# vim: ts=2:sw=2:tw=80:nowrap

import copy

def writevars( F, vardict ):
  if not F:
    return
  for i in vardict.items():
    F.write( '{K} = {V}\n'.format(K=str(i[0]),V=repr(i[1])) )

def readvars( F ):
  if not F:
    return None
  exec(F)
  retval = copy.copy( locals() )
  retval.pop('F')
  return retval
