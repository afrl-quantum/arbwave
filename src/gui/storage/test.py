#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap

import sys
sys.path.append('..')

import gtk
from storage.gtk_tools import *

class win(gtk.Window):
  def __init__(self, parent=None):
    gtk.Window.__init__(self)
    self.set_title("test")
    try:
      self.set_screen(parent.get_screen())
    except:
      self.connect("destroy", lambda *w: gtk.main_quit())
    
    mb = gtk.MenuBar()
    self.add(mb)
    fi = gtk.MenuItem("_File")
    mb.append(fi)
    fi.set_use_underline(True)
    fim = gtk.Menu()
    fi.set_submenu( fim )
    oi = gtk.ImageMenuItem(stock_id=gtk.STOCK_OPEN)
    oi.connect('activate', gtk_open_handler, self)
    si = gtk.ImageMenuItem(stock_id=gtk.STOCK_SAVE)
    si.connect('activate', gtk_save_handler, self)
    fim.append(oi)
    fim.append(si)

    self.show_all()

    self.variables = {'a': 42, 'b' : 42.42}

  def getvars(self):
    return self.variables

  def setvars(self, vdict):
    for v in self.variables:
      try:
        self.variables[v] = vdict[v]
      except:
        pass

if __name__ == '__main__':
  w = win()
  gtk.main()

