# vim: ts=2:sw=2:tw=80:nowrap
from pygraph.classes.digraph import digraph
from pygraph.algorithms.minmax import shortest_path

G = digraph()
registered = dict()

def register_converter( _from, to, func ):
  if not G.has_node( _from ):
    G.add_node( _from )
  if not G.has_node( to ):
    G.add_node( to )

  G.add_edge( (to,_from) )
  registered[ (_from,to) ] = func

def conversion_path( _from, to ):
  if _from == to:
    return [ lambda v : v ] # in == out, no conversion necessary

  path = shortest_path(G, to)[0]
  conversion_functions = list()
  while _from:
    to = path.get(_from,None)
    if to is None: break
    conversion_functions.append( registered[(_from, to)] )
    _from = to

  return conversion_functions
