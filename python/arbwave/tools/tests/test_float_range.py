#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from .. import float_range

class FloatRange(unittest.TestCase):
  def test_float_range_extrema(self):
    fr = float_range.float_range(0.1,5.1)
    self.assertEqual(min(fr), 0.1)
    self.assertEqual(max(fr), 5.1)

  def test_float_range_contains(self):
    fr = float_range.float_range(0.1,5.1)
    self.assertIn(.2, fr, '"in float_range" failed')
    self.assertNotIn(-.2, fr, '"in float_range" failed')
    self.assertNotIn(5.2, fr, '"in float_range" failed')
