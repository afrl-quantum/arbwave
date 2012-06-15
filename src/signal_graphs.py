# vim: ts=2:sw=2:tw=80:nowrap

from pygraph.classes.digraph import digraph
from pygraph.algorithms.minmax import *

def build_graph( *nodes, **signals ):
  g = digraph()
  g.add_nodes(nodes)

  for sig in signals.items():
    N0, N1 = sig[0], sig[1]['dest']
    if N0 not in g:
      g.add_node(N0)
    if N1 not in g:
      g.add_node(N1)
    g.add_edge( (N0, N1) )

  return g


def accessible_clocks( terms, clocks, signals ):
  T = set([ str(ti)  for ti in terms])
  C = clocks.representation().keys()
  S = signals.representation()

  g = build_graph( *C, **S )
  short_paths = { clk:shortest_path(g,clk) for clk in C }
  return [ clk for clk in C if T.intersection(short_paths[clk][0].keys()) ]


def shortest_paths( *clocks, **signals ):
  g = build_graph( *clocks, **signals )
  return { clk : shortest_path(g,clk)  for clk in clocks }


def nearest_terminal( clk, terms, shortest_paths ):
  """
  We need to find the terminal that uses the shortest signal path from the clock
  """
  nodes, dist = shortest_paths[clk]
  t_dist = { k : dist[k]  for k in terms.intersection( nodes.keys() ) }
  t_dist = t_dist.items()
  t_dist.sort( key=lambda i:i[1] )
  # elements in t_dist are like (<terminal-name>, <distance>)
  # the first element is the best
  return t_dist[0][0]