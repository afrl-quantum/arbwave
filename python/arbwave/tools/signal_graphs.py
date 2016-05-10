# vim: ts=2:sw=2:tw=80:nowrap

from .graphs import DiGraph

def build_graph( signals, *nodes ):
  """
  Create a graph from signals to terminals.
  """
  g = DiGraph()
  g.add_nodes_from(tuple(set(nodes))) # just to make sure it is unique

  for src, dst in signals:
    if not g.has_node(src):
      g.add_node(src)
    if not g.has_node(dst):
      g.add_node(dst)
    g.add_edge(src, dst)

  return g


def accessible_clocks( terms, clocks, signals ):
  """
  Create a list of all clocks that are accessible by the given terminals through
  the given signals.
  """
  C = clocks.representation()
  S = signals.representation()
  g = build_graph( S, *C )
  T = set([ str(ti)  for ti in terms]).intersection( g.nodes() )

  valid_clocks = list()
  for clk in C:
    for term in T:
      if g.has_path(clk, term):
        valid_clocks.append( clk )
        break
  return valid_clocks


def nearest_terminal( clk, terms, graph ):
  """
  We need to find the terminal that uses the shortest signal path from the clock
  """
  T = terms.intersection( graph.nodes() )
  return graph.get_nearest_terminal(clk, T)
