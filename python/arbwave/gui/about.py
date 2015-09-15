# vim: ts=2:sw=2:tw=80:nowrap

PROGNAME = 'Arbitrary Wavform Generator'
AUTHORS = [
  'Spencer E. Olson (Air Force Research Laboratory)',
  'Brian Kasch (Space Dynamics Laboratory)',
  'Ian Hage (Universities Space Research Association)',
]

import gtk
from .. import version

def show():
  dialog = gtk.AboutDialog()
  dialog.set_name(PROGNAME)
  dialog.set_version( 'v'+version.version() )
  dialog.set_authors(AUTHORS)
  dialog.set_license(
    'Arbitrary Waveform Generator:\n'
    '  Timing and control program for data acquisition\n'
    '\n'
    'This software is released under the GPL v3 license\n'
    '\n'
    ' Public Domain Contributions 2012-2015 United States Government '
    ' as represented by the U.S. Air Force Research Laboratory.\n'
    ' Portions copyright Copyright (C) 2012 Space Dynamics Laboratory\n'
    ' Portions copyright Copyright (C) 2015 Universities Space Research Association\n'
  )
  dialog.set_wrap_license(80)
  dialog.set_copyright("\302\251 Cold Atom Navigation Laboratory")
  dialog.set_website("http://www.cold-atoms.afrl.af.mil./")
  ## Close dialog on user response
  dialog.connect("response", lambda d, r: d.destroy())
  dialog.show()

