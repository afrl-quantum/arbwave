# vim: ts=2:sw=2:tw=80:nowrap

PROGNAME = 'Arbitrary Wavform Generator'
AUTHORS = [
  'Spencer E. Olson',
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
    '   - Co-authored by Air Force Research Laboraory\n'
    '     (U.S. Government)\n'
    '\n'
    'This software is released under the GPL v3 license'
  )
  dialog.set_wrap_license(80)
  dialog.set_copyright("\302\251 Cold Atom Navigation Laboratory")
  dialog.set_website("http://www.cold-atoms.afrl.af.mil./")
  ## Close dialog on user response
  dialog.connect("response", lambda d, r: d.destroy())
  dialog.show()

