# vim: ts=2:sw=2:tw=80:nowrap

class Dict(dict):
  """
  Simple dictionary that provides dictionary access using attributes.
  """
  def __init__(self, *a, **kw):
    super(Dict,self).__init__(*a,**kw)
    self.__dict__ = self

  def reverse(self):
    """
    Returns a dictionary with the key/value roles reversed.  Obviously, if
    values are not unique, this function is not reversible.
    """
    return Dict({v:k for k,v in self.iteritems()})
