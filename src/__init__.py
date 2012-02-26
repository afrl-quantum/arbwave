# vim: ts=2:sw=2:tw=80:nowrap
"""
Arbitrary waveform generator for digital and analog signals.
"""

import version

def main():
  import gui
  import gtk
  gui.ArbWave()
  gtk.main()

