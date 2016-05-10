# vim: ts=2:sw=2:tw=80:nowrap
from gi.repository import Gtk as gtk

from dispatcher import TreeModelDispatcher


class Hosts(TreeModelDispatcher, gtk.ListStore):
  PREFIX    = 0
  HOST      = 1
  DEFAULT   = 2
  #PROTECTED = 3

  def __init__(self, **kwargs):
    # FIXME:  it will likely become necessary to also specify the base Pyro URI
    super(Hosts,self).__init__(
      model=gtk.ListStore,
      model_args=(
        str,  # prefix
        str,  # host
        bool, # default
        #bool, # protected (default is False)
      ),
      **kwargs
    )

    self.reset_to_default()

  def reset_to_default(self):
    self.clear()
    self.append( ( 'local', 'localhost', True ) )


  def dict(self):
    D = dict()
    default = self[0][Hosts.PREFIX]
    for i in iter(self):
      if not (i[Hosts.PREFIX] and i[Hosts.HOST]):
        continue # skip rows that are not yet complete
      D[ i[Hosts.PREFIX] ] = i[Hosts.HOST]
      if i[Hosts.DEFAULT]:
        default = i[Hosts.PREFIX]
    D['__default__'] = default
    return D

  def load(self, D):
    self.clear()
    D = D.copy()
    default = D.pop('__default__', 'local')
    for i in D.items():
      self.append([
        i[0], #prefix
        i[1], #host
        i[0] == default,
      ])

  def representation(self):
    return self.dict()
