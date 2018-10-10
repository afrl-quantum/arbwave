# vim: ts=2:sw=2:tw=80:nowrap

class Device(object):
  """Base device class"""
  _pyro_ = True # For remote connections, this class must use pyro

  def __init__(self, name):
    self._name = name

  def __str__(self):
    return self._name

  @property
  def device(self):
    """
    Just to make it easier to query device as an attribute too.
    """
    return self

  @property
  def name(self):
    return self._name

  @property
  def device_str(self):
    """
    Just to make it easier to query device name with same interface as for
    channels.
    """
    return self._name

  @property
  def config_template(self):
    return self.get_config_template()

  def get_config_template(self):
    return dict()

  @property
  def prefix(self):
    """
    Parse the name of the device to return the prefix of the device.  The prefix
    is composed of [host_prefix:]driver_prefix
    """
    return self._name.partition('/')[0]

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
