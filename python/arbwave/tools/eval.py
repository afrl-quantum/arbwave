# vim: ts=2:sw=2:tw=80:nowrap

def evalIfNeeded( s, G, L=dict() ):
  if type(s) is str:
    try:
      return eval( s, G, L )
    except Exception as e:
      raise RuntimeError('Could not evaluate python text: "{}"\n{}'.format(s,e))
  else:
    return s
