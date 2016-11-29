# vim: ts=2:sw=2:tw=80:nowrap
"""
Simple file to help select between either igraph or networkx.  igraph has been
shown to be _significantly_ faster than networkx, but networkx appears to be
much more distributed.

This file provides a DiGraph class that is layered on top of either
igraph.Graph(directed=True) if igraph is found, or a networkx.DiGraph

Each of these classes is mildly extended in order to support Arbwave needs.
"""

try:
  import igraph
  inf = float('inf')

  class DiGraph(igraph.Graph):
    def __init__(self, *a, **kw):
      super(DiGraph,self).__init__(*a, **kw)
      if not self.is_directed():
        if a or kw:
          # This should only occur if a pickling did not complete correctly
          raise RuntimeError('Graph not initialized as directed')
        self.to_directed()

    def add_node(self, *a, **kw):
      return self.add_vertex(*a, **kw)

    def add_nodes_from(self, *a, **kw):
      return self.add_vertices(*a, **kw)


    def has_node(self, name):
      return len(self.vs) != 0 and name in self.vs['name']

    def nodes(self):
      return self.vs['name']

    def edges(self):
      # This is not an efficient way of using igraph
      return [(self.vs[i.source]['name'],
               self.vs[i.target]['name'])
              for i in self.es]

    def has_path(self, source, target):
      return self.shortest_paths(source, target)[0][0] < inf

    def get_nearest_terminal(self, source, terminals):
      """
      Body of nearest_terminal
        terminals : a set of all terminals that are also nodes in this graph
      """
      L = self.get_all_shortest_paths(source, terminals)
      if not L:
        return None
      L.sort( key = lambda i : len(i) )
      return self.vs[ L[0][-1] ]['name']

    def shortest_path(self, source, target):
      path = self.get_shortest_paths(source, target)[0]
      if not path:
        raise RuntimeError('No path between {} and {}'.format(source, target))
      return self.vs[path]['name']

    def topological_sorted_nodes(self):
      return [self.vs[i]['name'] for i in self.topological_sorting()]

    def predecessors_iter(self, vertex):
      for vi in self.predecessors(vertex):
        yield self.vs[vi]['name']


except:
  import networkx

  class DiGraph(networkx.DiGraph):
    def has_path(self, source, target):
      try:
        return bool( networkx.shortest_path(self, source, target) )
      except networkx.NetworkXNoPath:
        return False

    def get_nearest_terminal(self, source, terminals):
      """
      Body of nearest_terminal
        terminals : a set of all terminals that are also nodes in this graph
      """
      D = networkx.shortest_path(self, source)
      L = [ v for k,v in networkx.shortest_path(self, source).iteritems()
            if k in terminals ]
      if not L:
        return None
      L.sort( key = lambda i : len(i) )
      return L[0][-1]

    def shortest_path(self, source, target):
      return networkx.shortest_path(self, source, target)

    def topological_sorted_nodes(self):
      return networkx.topological_sort(self)
