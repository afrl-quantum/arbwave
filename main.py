#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import gtk
import gui

def main():
  gui.ArbWave()
  gtk.main()

if __name__ == '__main__':
  main()

