# vim: ts=2:sw=2:tw=80:nowrap
from ..graphs import DiGraph

# We do not need to use the dynamically assigned DiGraph class since this
# version compatibilty stuff happens only on the frontend--we'll use whatever
# version of DiGraph exists at startup.
G = DiGraph()
registered = dict()

def register_converter( _from, to, func ):
  if not G.has_node( _from ):
    G.add_node( _from )
  if not G.has_node( to ):
    G.add_node( to )

  G.add_edge(_from, to)
  registered[ (_from,to) ] = func

def conversion_path( _from, to ):
  if _from == to:
    return [ lambda v : v ] # in == out, no conversion necessary

  path = G.shortest_path(_from, to)[1:]
  conversion_functions = list()
  for to in path:
    conversion_functions.append( registered[(_from, to)] )
    _from = to

  return conversion_functions
