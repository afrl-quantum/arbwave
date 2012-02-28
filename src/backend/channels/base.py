# vim: ts=2:sw=2:tw=80:nowrap

class Base:
  """Base channel class"""
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name

