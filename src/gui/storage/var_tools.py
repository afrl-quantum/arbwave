# vim: ts=2:sw=2:tw=80:nowrap

import pprint

def writevars( F, vardict ):
  if not F:
    return
  for i in vardict.items():
    F.write( '{K} = \\\n'.format(K=str(i[0])) )
    if type(i[1]) is str and len(i[1]) > 80:
      F.write('"""'+i[1]+'"""\n')
    else:
      pprint.pprint(i[1], F )
    F.write('\n')

def readvars( source, globals=globals(), **locals ):
  if not source:
    return None
  exec source in globals, locals
  return locals
