#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os, itertools
from .. import signal_graphs

THIS_DIR = os.path.dirname(__file__)

gnuplot_test_file = os.path.join(THIS_DIR,'signals_test_results.txt')

class rep_class(object):
  def __init__(self, obj):
    self.obj = obj
  def representation(self):
    return self.obj

class SignalGraphs(unittest.TestCase):
  terminals = [
    'PFI5', 'TRIG/0', 'TRIG/1', 'TRIG/2', 'TRIG/3', 'TRIG/4', 'TRIG/5', 'TRIG/6'
  ]

  signals = {
    ('vp/Dev0/A/13', 'TRIG/1'): {'invert': False},
    ('vp/Dev0/A/14', 'TRIG/2'): {'invert': False},
    ('External/cable0', 'PFI5'): {'invert': False},
    ('vp/Dev0/A/15', 'External/cable0'): {'invert': False},
  }

  clocks = {
    'vp/Dev0/A/13'        : {'divider': {'type': int, 'value': 2}},
    'vp/Dev0/A/15'        : {'divider': {'type': int, 'value': 2}},
    'vp/Dev0/Internal_XO' : {'scan_rate': {'type': float, 'value': 20000000.0}},
  }

  all_nodes = set(clocks.keys()).union(set( itertools.chain(*signals.keys()) ))

  all_edges = set([
    ('vp/Dev0/A/13', 'TRIG/1'),
    ('vp/Dev0/A/14', 'TRIG/2'),
    ('vp/Dev0/A/15', 'External/cable0'),
    ('External/cable0', 'PFI5'),
  ])

  accessible_clocks = ['vp/Dev0/A/13', 'vp/Dev0/A/15']

  nearest_terminals = [
    ('vp/Dev0/A/13', 'TRIG/1'),
    ('vp/Dev0/Internal_XO', None),
    ('vp/Dev0/A/15', 'PFI5'),
  ]

  def test_build_graph(self):
    g = signal_graphs.build_graph( self.signals, *self.clocks )
    # first, test nodes
    graph_nodes = g.nodes()
    graph_nodes.sort()
    original_graph_nodes = list(self.all_nodes)
    original_graph_nodes.sort()
    self.assertEqual(original_graph_nodes, graph_nodes)

    # second, test edges
    graph_edges = g.edges()
    graph_edges.sort()
    original_graph_edges = list(self.all_edges)
    original_graph_edges.sort()
    self.assertEqual(original_graph_edges, graph_edges)

  def test_accessible_clocks(self):
    A = signal_graphs.accessible_clocks(self.terminals,
                                        rep_class(self.clocks),
                                        rep_class(self.signals))
    self.assertEqual(self.accessible_clocks, A)

  def test_nearest_terminal(self):
    g = signal_graphs.build_graph( self.signals, *self.clocks )
    T = set( self.terminals )

    nearest = [
      (clk,signal_graphs.nearest_terminal(clk, T, g)) for clk in self.clocks
    ]

    self.assertEqual(self.nearest_terminals, nearest)
