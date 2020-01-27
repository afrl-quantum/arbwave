# vim: ts=2:sw=2:tw=80:nowrap
"""
Test subdevice.enum module
"""

import unittest
from os import path
from physical import unit
import comedi

from ... import sim
from .. import enum

THIS_DIR = path.dirname( __file__ )

# typical import of physical units
physical_import = """\
from physical.constant import *
from physical.unit import *
from physical import unit
"""


class EnumBase(unittest.TestCase):
  def setUp(self):
    self.csim = sim.ComediSim()

  def tearDown(self):
    self.csim.remove_from_clib()

  # this will change as we simulate more parts of the hardware
  # just make sure that this matches the simulated hardware for Dev0
  subdev_iterator_answer = ([1], [], [7, 10], [])
  def test_subdev_iterator(self):
    d0 = comedi.open( '/dev/comedi0' )
    self.assertEqual( comedi.get_board_name(d0), b'pxi-6733' )
    L = ( list( enum.subdev_iterator( d0, comedi.SUBD_AO ) ),
          list( enum.subdev_iterator( d0, comedi.SUBD_DO ) ),
          list( enum.subdev_iterator( d0, comedi.SUBD_DIO ) ),
          list( enum.subdev_iterator( d0, comedi.SUBD_COUNTER ) ),
        )
    self.assertEqual(L,self.subdev_iterator_answer)


  # this will change as we simulate more parts of the hardware
  # just make sure that this matches the simulated hardware for Dev0
  useful_subdev_answer_AO = [ ('comedi_t_ptr(2)',1) ]
  useful_subdev_answer_DO = [ ]
  useful_subdev_answer_DIO= [ ('comedi_t_ptr(2)',2) ]
  def test_get_useful_subdev_list(self):
    d0 = comedi.open( '/dev/comedi2' ) # simulate for 6229 for diversity
    self.assertEqual( comedi.get_board_name(d0), b'pci-6229' )

    ret = enum.get_useful_subdev_list( d0, comedi.SUBD_AO )
    ret = [ (str(d0), i)  for i in ret ]
    self.assertEqual( ret, self.useful_subdev_answer_AO )

    ret = enum.get_useful_subdev_list( d0, comedi.SUBD_DO )
    ret = [ (str(d0), i)  for i in ret ]
    self.assertEqual( ret, self.useful_subdev_answer_DO )

    ret = enum.get_useful_subdev_list( d0, comedi.SUBD_DIO )
    ret = [ (str(d0), i)  for i in ret ]
    self.assertEqual( ret, self.useful_subdev_answer_DIO )


  #def test_get_useful_subdevices(self):
  #  # FIXME: implement this
  #  self.assertEqual( 0, 1 )
