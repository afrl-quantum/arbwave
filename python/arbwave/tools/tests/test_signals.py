#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from .. import signals

THIS_DIR = os.path.dirname(__file__)

gnuplot_test_file = os.path.join(THIS_DIR,'signals_test_results.txt')

class Signals(unittest.TestCase):
  def test_gnuplot_output(self):
    with open(gnuplot_test_file) as f:
      original_data = f.read()

    fake = signals._FakeStuffCreator()
    self.assertEqual( original_data, fake.test_gnuplot() )
