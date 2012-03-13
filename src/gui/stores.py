# vim: ts=2:sw=2:tw=80:nowrap

import gtk

import edit


class TreeModelDispatcher:
  """
  Simple signal aggregation for any changes to a single 'changed' signal.
  """
  def __init__(self, Model, changed=None):
    self.Model = Model
    if changed:
      self.connect( 'changed', changed )

  def connect(self, signal, callback, *args, **kwargs):
    if signal == 'changed':
      for i in [
        ('row-changed',    self.row_changed   ),
        ('row-deleted',    self.row_deleted   ),
        ('row-inserted',   self.row_inserted  ),
        ('rows-reordered', self.rows_reordered),
      ]:
        self.Model.connect(self, i[0],i[1], callback, *args, **kwargs )
    else:
      self.Model.connect(self, signal, callback, *args, **kwargs)

  def row_changed(self, model, path, iter,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def row_deleted(self, model, path,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def row_inserted(self, model, path, iter,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def rows_reordered(self, model, path, iter, new_order,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)



class Channels(TreeModelDispatcher, gtk.ListStore):
  LABEL   =0
  DEVICE  =1
  SCALING =2
  VALUE   =3
  ENABLE  =4

  def __init__(self, **kwargs):
    gtk.ListStore.__init__(self,
      str,  # Label
      str,  # device
      str,  # scaling
      str,  # value
      bool, # enable
    )

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)


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


class Waveforms(TreeModelDispatcher, gtk.TreeStore):
  CHANNEL =0
  TIME    =1
  DURATION=2
  VALUE   =3
  ENABLE  =4
  SCRIPT  =5
  ASYNC   =6

  def __init__(self, **kwargs):
    gtk.TreeStore.__init__(self,
      str,  # channel
      str,  # Time
      str,  # duration
      str,  # value
      bool, # enable
      str,  # script
      bool, # async
    )

    TreeModelDispatcher.__init__(self, gtk.TreeStore, **kwargs)


  def list(self):
    L = list()
    for i in iter(self):
      if i.parent is not None:
        raise RuntimeError('Parented item at root-level of waveform tree')
      D = dict()
      D['group-label' ] = i[Waveforms.CHANNEL]
      D['time'        ] = i[Waveforms.TIME]
      D['duration'    ] = i[Waveforms.DURATION]
      D['script'      ] = i[Waveforms.SCRIPT]
      D['enable'      ] = i[Waveforms.ENABLE]
      D['asynchronous'] = i[Waveforms.ASYNC]
      l = D['elements'] = list()
      for j in i.iterchildren():
        l.append({
          'channel' : j[Waveforms.CHANNEL],
          'time'    : j[Waveforms.TIME],
          'duration': j[Waveforms.DURATION],
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
        (i['group-label'], i['time'], i['duration'], None,
         i['enable'], i['script'], i['asynchronous']) )
      for e in i['elements']:
        self.append( parent,
          (e['channel'], e['time'], e['duration'], e['value'],
           e['enable'], None, None) )

  def representation(self):
    return self.list()


class Signals(TreeModelDispatcher, gtk.ListStore):
  SOURCE  =0
  DEST    =1
  INVERT  =2

  def __init__(self, **kwargs):
    gtk.ListStore.__init__(self,
      str,  # Source
      str,  # Destination
      bool, # invert-polarity
    )

    TreeModelDispatcher.__init__(self, gtk.ListStore, **kwargs)


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
  def __init__(self, text='', title='Script', parent=None,
                changed=None, *changed_args, **changed_kwargs):
    self.editor = None
    self.text   = text
    self.title  = title
    self.parent = parent
    self.onchange = None

    if changed:
      self.connect( 'changed', changed, *changed_args, **changed_kwargs )

  def __str__(self):
    return self.text

  def clear(self):
    self.set_text('')

  def set_text(self, t):
    self.text = t
    if self.editor:
      self.editor.set_text( t )
    if self.onchange:
      self.onchange['callable'](
        self, *self.onchange['args'], **self.onchange['kwargs']
      )

  def get_text(self):
    return self.text

  def load(self, t):
    self.set_text(t)

  def representation(self):
    return str(self)

  def connect(self, signal, callback, *args, **kwargs):
    if signal == 'changed':
      self.onchange = {
        'callable'  : callback,
        'args'      : args,
        'kwargs'    : kwargs,
      }
    else:
      raise TypeError('unkown signal ' + signal)

  def edit(self):

    def unset_editor(*args):
      self.editor = None

    if not self.editor:
      self.editor = edit.script.Editor( self.title, self.parent, target=self )
      self.editor.connect('destroy', unset_editor)

    self.editor.present()

