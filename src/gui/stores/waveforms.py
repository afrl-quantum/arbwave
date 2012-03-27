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
        (i['group-label'], i['time'], i['duration'], '',
         i['enable'], i['script'], i['asynchronous']) )
      for e in i['elements']:
        self.append( parent,
          (e['channel'], e['time'], e['duration'], e['value'],
           e['enable'], None, None) )

  def representation(self):
    return self.list()
