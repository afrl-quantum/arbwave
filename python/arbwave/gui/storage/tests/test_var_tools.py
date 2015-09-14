#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import unittest, os
from tempfile import mkstemp
from ..var_tools import readvars, writevars

class ReadWriteVars(unittest.TestCase):
  original_dict = {
    'A' : 'a',
    'B' : 'b',
    'C' : 'c',
    'D' : 'd',
  }

  def setUp(self):
    self.tmpfilename = mkstemp()[1]

  def tearDown(self):
    os.unlink( self.tmpfilename )
    del self.tmpfilename

  def runTest(self):
    F = open( self.tmpfilename, 'w')
    writevars(F, self.original_dict)
    F.close()

    F = open( self.tmpfilename )
    read_dict = readvars(F)
    F.close()
    self.assertEqual( self.original_dict, read_dict )
