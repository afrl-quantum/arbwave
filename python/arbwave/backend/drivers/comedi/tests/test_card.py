# vim: ts=2:sw=2:tw=80:nowrap
"""
Test card module
"""

import unittest
from os import path
import copy
from physical import unit

from .. import sim
from .. import card
from .. import ctypes_comedi as clib

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

  # this will change as we simulate more parts of the hardware
  # just make sure that this matches the simulated hardware for Dev0
  subdev_iterator_answer = ([1], [], [], [])
  def test_subdev_iterator(self):
    d0 = clib.comedi_open( '/dev/comedi0' )
    L = ( list( card.subdev_iterator( d0, clib.COMEDI_SUBD_AO ) ),
          list( card.subdev_iterator( d0, clib.COMEDI_SUBD_DO ) ),
          list( card.subdev_iterator( d0, clib.COMEDI_SUBD_DIO ) ),
          list( card.subdev_iterator( d0, clib.COMEDI_SUBD_COUNTER ) ),
        )
    self.assertEqual(L,self.subdev_iterator_answer)

  def test_get_useful_subdevices(self):
    # FIXME: implement this
    self.assertEqual( 0, 1 )

  def test_Card_get_card_number(self):
    self.assertEqual( card.Card.get_card_number('/dev/comedi0'), '0' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi1'), '1' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi2'), '2' )
    self.assertEqual( card.Card.get_card_number('/dev/comedi3'), '3' )
