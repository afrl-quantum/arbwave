# vim: ts=2:sw=2:tw=80:nowrap

class Device:
  """Base device class"""
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name

  def get_config_template(self):
    return dict()

  def prefix(self):
    return self.name.partition('/')[0]
