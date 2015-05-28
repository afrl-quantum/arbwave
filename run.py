#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import sys, os
PYDIR = os.path.join( os.path.dirname( __file__ ), 'python' )
sys.path.insert(0, PYDIR)

import arbwave

if __name__ == '__main__':
  arbwave.main()
