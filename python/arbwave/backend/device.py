# vim: ts=2:sw=2:tw=80:nowrap

class Device(object):
  """Base device class"""
  _pyro_ = True # For remote connections, this class must use pyro

  def __init__(self, name):
    self.name = name

  def __str__(self):
    return self.name

  def get_config_template(self):
    return dict()

  @property
  def prefix(self):
    """
    Parse the name of the device to return the prefix of the device.  The prefix
    is composed of [host_prefix:]driver_prefix
    """
    return self.name.partition('/')[0]

  def start(self):
    """
    Starts a device.  This should be overridden by inheriting classes.
    """
    pass

  def wait(self):
    """
    Waits on device task.  This should be overridden by inheriting classes.
    """
    pass

  def stop(self):
    """
    Stops a device.  This should be overridden by inheriting classes.
    """
    pass
