#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from .. import generic

def get_conversion_path_str(_from, to):
  path = conversion_path(_from, to)
  return [ (f.__module__.rpartition('.')[-1], f.__name__) for f in path ]

class Generic(unittest.TestCase):
  def test_empty_config_tree(self):
    """
    testing loading with empty config-tree:
    """

    data0 = { 'clock' : { }, }
    g = generic.Generic()
    g.load( data0 )
    # ... no complaints so far

    # testing representation
    self.assertEqual(data0, g.representation())

  def test_complex_config_tree(self):
    """
    testing loading with more complicated config-tree
    """
    data0 = {
      'Dev1' : {
        'out' : {
          'param0' : { 'type': int, 'range':range(10), 'value': 2 },
          'param1' : { 'type': str, 'range':['a','b'], 'value': 'b' },
        },
        'in' : {
          'param2' : { 'type': bool, 'range':None, 'value': False },
          'param3' : { 'type': float, 'range':range(-10,30), 'value': 0.3 },
        },
      },
    }

    g = generic.Generic(store_range=True)
    g.load( data0 )
    # ... no complaints so far

    # testing representation
    self.assertEqual(data0, g.representation())

  def test_complex_config_tree_w_enable(self):
    """
    testing loading with more complicated config-tree
    """
    data0 = {
      'Dev1' : {
        'enable' : True,
        'parameters' : {
          'out' : {
            'enable' : True,
            'parameters' : {
              'param0' : { 'enable':True, 'type': int, 'range':range(10), 'value': 2 },
              'param1' : { 'enable':True, 'type': str, 'range':['a','b'], 'value': 'b' },
            },
          },
          'in' : {
            'enable': True,
            'parameters' : {
              'param2' : { 'enable':True, 'type': bool, 'range':None, 'value': False },
              'param3' : { 'enable':True, 'type': float, 'range':range(-10,30), 'value': 0.3 },
            }
          },
        },
      },
    }

    g = generic.Generic(store_range=True,use_enable=True)
    g.load( data0 )
    # ... no complaints so far

    # testing representation
    self.assertEqual(data0, g.representation())

  def test_listofparams_config_tree_w_enable(self):
    """
    testing loading with only a list of parameters
    """
    data0 = {
      'param2' : { 'enable':True, 'type': bool, 'range':None, 'value': False },
      'param3' : { 'enable':True, 'type': float, 'range':range(-10,30), 'value': 0.3 },
    }
    g = generic.Generic(store_range=True, use_enable=True)
    g.load( data0 )
    # ... no complaints so far

    # testing representation
    self.assertEqual(data0, g.representation())


  def test_complex_config_tree_w_enable_w_keeporder(self):
    """
    testing loading with more complicated config-tree with order maintained
    """
    data0 = {
      'Dev0' : {
        'enable' : True,
        'order'  : 1,
        'parameters' : {
          'out' : {
            'enable' : True,
            'order'  : 0,
            'parameters' : {
              'param0' : { 'order':1, 'enable':True, 'type': int, 'range':range(10), 'value': 2 },
              'param1' : { 'order':0, 'enable':True, 'type': str, 'range':['a','b'], 'value': 'b' },
            },
          },
          'in' : {
            'enable': True,
            'order'  : 1,
            'parameters' : {
              'param2' : { 'order':1, 'enable':True, 'type': bool, 'range':None, 'value': False },
              'param3' : { 'order':0, 'enable':True, 'type': float, 'range':range(-10,30), 'value': 0.3 },
            }
          },
        },
      },
      'Dev1' : {
        'enable' : True,
        'order'  : 0,
        'parameters' : {
          'out' : {
            'enable' : True,
            'order'  : 0,
            'parameters' : {
              'param0' : { 'order':1, 'enable':True, 'type': int, 'range':range(10), 'value': 2 },
              'param1' : { 'order':0, 'enable':True, 'type': str, 'range':['a','b'], 'value': 'b' },
            },
          },
          'in' : {
            'enable': True,
            'order'  : 1,
            'parameters' : {
              'param2' : { 'order':1, 'enable':True, 'type': bool, 'range':None, 'value': False },
              'param3' : { 'order':0, 'enable':True, 'type': float, 'range':range(-10,30), 'value': 0.3 },
            }
          },
        },
      },
    }

    g = generic.Generic(store_range=True,use_enable=True,keep_order=True)
    g.load( data0 )
    # ... no complaints so far

    # testing representation
    self.assertEqual(data0, g.representation())
