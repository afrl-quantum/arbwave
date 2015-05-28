# vim: ts=2:sw=2:tw=80:nowrap

import pprint
import repr as reprlib

# tweak the repr used by pprint
class MyRepr(reprlib.Repr):
  """
  A custom version of repr that does not print <type 'int'> for native types
  like int, float, bool, str.
  """
  def __init__(self, *args, **kwargs):
    reprlib.Repr.__init__(self, *args, **kwargs)
    self.maxother=100
  def repr_type(self,obj,level):
    return obj.__name__

# override the pprint version of repr
pprint.repr = MyRepr().repr


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
