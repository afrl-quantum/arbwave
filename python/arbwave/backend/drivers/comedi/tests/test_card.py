# vim: ts=2:sw=2:tw=80:nowrap
"""
Test card module
"""

import unittest
from os import path
import copy
from physical import unit
import comedi

from .. import sim
from .. import card

THIS_DIR = path.dirname( __file__ )

# typical import of physical units
physical_import = """\
from physical.constant import *
from physical.unit import *
from physical import unit
"""


class CardBase(unittest.TestCase):
  def setUp(self):
    self.csim = sim.ComediSim()

  def tearDown(self):
    self.csim.remove_from_clib()

  def test_Card_get_card_number(self):
    self.assertEqual( card.Card.get_card_number('/dev/comedi0'), '0' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi1'), '1' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi2'), '2' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi3'), '3' )
