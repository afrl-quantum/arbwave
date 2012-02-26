# vim: ts=2:sw=2:tw=80:nowrap

import gtk, gobject

class Channels(gtk.ListStore):
  def __init__(self):
    gtk.ListStore.__init__(self,
      gobject.TYPE_STRING,  # Label
      gobject.TYPE_STRING,  # device
      gobject.TYPE_STRING,  # value
      gobject.TYPE_BOOLEAN, #enabled
    )

  def dict(self):
    D = dict()
    for i in iter(self):
      D[ i[0] ] = i[1:]
    return D

  def load(self, D):
    for i in D:
      self.append( [i] + D[i] )

  def representation(self):
    return self.dict()


class Waveforms(gtk.TreeStore):
  def __init__(self):
    gtk.TreeStore.__init__(self,
      gobject.TYPE_STRING,  # channel
      gobject.TYPE_STRING,  # Time
      gobject.TYPE_STRING,  # value
      gobject.TYPE_BOOLEAN, #enabled
    )

  def load(self,config):
    # places the global people data into the list
    # we form a simple tree.
    for item in config.keys():
      parent = self.append( None, (item, None, None, True) )
      for task in config[item]:
        self.append( parent, (task[0], task[1], task[2], True) )


class Signals(gtk.ListStore):
  def __init__(self):
    gtk.ListStore.__init__(self,
      gobject.TYPE_STRING,  # Source
      gobject.TYPE_STRING,  # Destination
      gobject.TYPE_BOOLEAN, # invert-polarity
    )

  def list(self):
    return [ list(li)  for li in l ]

  def load(self, L):
    for i in L:
      self.append( i )
    
  def representation(self):
    return self.list()

