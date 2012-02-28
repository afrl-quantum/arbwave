# vim: ts=2:sw=2:tw=80:nowrap

import gtk

class Channels(gtk.ListStore):
  LABEL   =0
  DEVICE  =1
  SCALING =2
  VALUE   =3
  ENABLE  =4

  def __init__(self):
    gtk.ListStore.__init__(self,
      str,  # Label
      str,  # device
      str,  # scaling
      str,  # value
      bool, # enabled
    )

  def dict(self):
    D = dict()
    for i in iter(self):
      D[ i[0] ] = {
        'device'  : i[1],
        'scaling' : i[2],
        'value'   : i[3],
        'enabled' : i[4],
      }
    return D

  def load(self, D):
    for i in D.items():
      self.append([
        i[0],
        i[1]['device'],
        i[1]['scaling'],
        i[1]['value'],
        i[1]['enabled'],
      ])

  def representation(self):
    return self.dict()


class Waveforms(gtk.TreeStore):
  CHANNEL =0
  TIME    =1
  VALUE   =2
  ENABLE  =3
  SCRIPT  =4

  def __init__(self):
    gtk.TreeStore.__init__(self,
      str,  # channel
      str,  # Time
      str,  # value
      bool, # enabled
      str,  # script
    )

  def list(self):
    L = list()
    for i in iter(self):
      if i.parent is not None:
        raise RuntimeError('Parented item at root-level of waveform tree')
      D = dict()
      D['group-label'] = i[CHANNEL]
      D['script'] = i[SCRIPT]
      D['time-step'] = i[TIME]
      l = D['elements'] = list()
      for j in i.iterchildren():
        l.append({
          'channel' : j[CHANNEL],
          'time'    : j[TIME],
          'value'   : j[VALUE],
          'enabled' : j[ENABLED],
        })

      L.append( D )  # finish group by appending to list of groups

    return L

  def load(self,L):
    # places the global people data into the list
    # we form a simple tree.
    for i in L:
      parent = self.append( None,
        (i['group-label'], i['time-step'], None, i['enabled'], i['script'])
      )
      for e in i['elements']:
        self.append( parent,
          (e['channel'], e['time'], e['value'], e['enabled'], None)
        )

  def representation(self):
    return self.list()


class Signals(gtk.ListStore):
  SOURCE  =0
  DEST    =1
  INVERT  =2

  def __init__(self):
    gtk.ListStore.__init__(self,
      str,  # Source
      str,  # Destination
      bool, # invert-polarity
    )

  def list(self):
    L = list()
    for i in iter(self):
      L.append({
        'source'  : i[0],
        'dest'    : i[1],
        'invert'  : i[2],
      })
    return L

  def load(self, L):
    for i in L:
      self.append([
        i['source'],
        i['dest'],
        i['invert'],
      ])
    
  def representation(self):
    return self.list()

