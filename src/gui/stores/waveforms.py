# vim: ts=2:sw=2:tw=80:nowrap

import gtk

from dispatcher import TreeModelDispatcher

class Waveforms(TreeModelDispatcher, gtk.TreeStore):
  CHANNEL =0
  TIME    =1
  DURATION=2
  VALUE   =3
  ENABLE  =4
  SCRIPT  =5
  ASYNC   =6


  default_group = ( '', 't', '', '', True,   '', False )
  default_element=( '', 't', '', '', True, None, None  )

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

    self.kwargs = kwargs
    TreeModelDispatcher.__init__(self, gtk.TreeStore, **kwargs)


  def __del__(self):
    TreeModelDispatcher.__del__(self)


  def copy(self):
    new = Waveforms( **self.kwargs )
    new.load( self.representation() )
    return new


  def __str__(self):
    return 'Waveform/' + str(id(self))

  def __repr__(self):
    return str(self)

  def list_recursive(self, iter, store_path):
    L = list()
    for i in iter:
      D = dict()
      D['time'    ] = i[Waveforms.TIME]
      D['duration'] = i[Waveforms.DURATION]
      D['enable'  ] = i[Waveforms.ENABLE]
      D['path'    ] = self.get_path( i.iter )

      if self.iter_has_child( i.iter ):
        # is group
        D['group-label' ] = i[Waveforms.CHANNEL]
        D['script'      ] = i[Waveforms.SCRIPT]
        D['asynchronous'] = i[Waveforms.ASYNC]
        D['elements'    ] = self.list_recursive( i.iterchildren(), store_path )
      else:
        # is element
        D['channel'     ] = i[Waveforms.CHANNEL]
        D['value'       ] = i[Waveforms.VALUE]

      L.append( D )

    return L


  def list(self, store_path=False):
    return self.list_recursive( iter(self), store_path )


  def load_recursive(self, L, parent=None):
    for i in L:
      if 'channel' in i: # is element
        self.append( parent,
          (i['channel'], i['time'], i['duration'], i['value'],
           i['enable'], None, None) )
      else: # is group
        me = self.append( parent,
          (i['group-label'], i['time'], i['duration'], '',
           i['enable'], i['script'], i['asynchronous']) )
        self.load_recursive(i['elements'], me)


  def load(self,L):
    self.clear()
    self.load_recursive(L)


  def representation(self, store_path=False):
    return self.list(store_path)
