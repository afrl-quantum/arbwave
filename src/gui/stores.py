# vim: ts=2:sw=2:tw=80:nowrap

import gtk

import edit

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
      bool, # enable
    )

  def dict(self):
    D = dict()
    for i in iter(self):
      D[ i[0] ] = {
        'device'  : i[Channels.DEVICE],
        'scaling' : i[Channels.SCALING],
        'value'   : i[Channels.VALUE],
        'enable'  : i[Channels.ENABLE],
      }
    return D

  def load(self, D):
    self.clear()
    for i in D.items():
      self.append([
        i[0],
        i[1]['device'],
        i[1]['scaling'],
        i[1]['value'],
        i[1]['enable'],
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
      bool, # enable
      str,  # script
    )

  def list(self):
    L = list()
    for i in iter(self):
      if i.parent is not None:
        raise RuntimeError('Parented item at root-level of waveform tree')
      D = dict()
      D['group-label' ] = i[Waveforms.CHANNEL]
      D['script'      ] = i[Waveforms.SCRIPT]
      D['time-step'   ] = i[Waveforms.TIME]
      D['enable'      ] = i[Waveforms.ENABLE]
      l = D['elements'] = list()
      for j in i.iterchildren():
        l.append({
          'channel' : j[Waveforms.CHANNEL],
          'time'    : j[Waveforms.TIME],
          'value'   : j[Waveforms.VALUE],
          'enable'  : j[Waveforms.ENABLE],
        })

      L.append( D )  # finish group by appending to list of groups

    return L

  def load(self,L):
    self.clear()
    # places the global people data into the list
    # we form a simple tree.
    for i in L:
      parent = self.append( None,
        (i['group-label'], i['time-step'], None, i['enable'], i['script'])
      )
      for e in i['elements']:
        self.append( parent,
          (e['channel'], e['time'], e['value'], e['enable'], None)
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
        'source'  : i[Signals.SOURCE],
        'dest'    : i[Signals.DEST],
        'invert'  : i[Signals.INVERT],
      })
    return L

  def load(self, L):
    self.clear()
    for i in L:
      self.append([
        i['source'],
        i['dest'],
        i['invert'],
      ])
    
  def representation(self):
    return self.list()


class Script:
  def __init__(self, text='', title='Script', parent=None, test_locals=dict()):
    self.editor = None
    self.text   = text
    self.title  = title
    self.parent = parent
    self.test_locals = test_locals

  def __str__(self):
    return self.text

  def clear(self):
    self.set_text('')

  def set_text(self, t):
    self.text = t
    if self.editor:
      self.editor.set_text( t )

  def get_text(self):
    return self.text

  def load(self, t):
    self.set_text(t)

  def representation(self):
    return str(self)

  def edit(self):

    def unset_editor(*args):
      self.editor = None

    if not self.editor:
      self.editor = edit.script.Editor( self.title, self.parent, target=self )
      self.editor.connect('destroy', unset_editor)

    self.editor.present()

