#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from .. import conversion_path

def get_conversion_path_str(_from, to):
  path = conversion_path(_from, to)
  return [ (f.__module__.rpartition('.')[-1], f.__name__) for f in path ]

class Compatibility(unittest.TestCase):
  short_path = [ ('from_0_1_2', 'to_0_1_3') ]

  long_path = [
    ('from_0_1_2', 'to_0_1_3'),
    ('from_0_1_3', 'to_0_1_4'),
    ('from_0_1_4', 'to_0_1_5'),
    ('from_0_1_5', 'to_0_1_6'),
    ('from_0_1_6', 'to_0_1_7'),
    ('from_0_1_7', 'to_0_1_8'),
  ]

  def test_short_conversion_path(self):
    path_str = get_conversion_path_str('0.1.2', '0.1.3')
    self.assertEqual( self.short_path, path_str )

  def test_long_conversion_path(self):
    path_str = get_conversion_path_str('0.1.2', '0.1.8')
    self.assertEqual( self.long_path, path_str )
