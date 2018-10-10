# vim: ts=2:sw=2:tw=80:nowrap

import Pyro4

class Device(object):
  """Base device class"""

  def __init__(self, name):
    self._name = name

  def __str__(self):
    return self._name

  @Pyro4.expose
  @property
  def device(self):
    """
    Just to make it easier to query device as an attribute too.
    """
    return self

  @Pyro4.expose
  @property
  def name(self):
    return self._name

  @Pyro4.expose
  @property
  def device_str(self):
    """
    Just to make it easier to query device name with same interface as for
    channels.
    """
    return self._name

  @Pyro4.expose
  @property
  def config_template(self):
    return self.get_config_template()

  @Pyro4.expose
  def get_config_template(self):
    return dict()

  @Pyro4.expose
  @property
  def prefix(self):
    """
    Parse the name of the device to return the prefix of the device.  The prefix
    is composed of [host_prefix:]driver_prefix
    """
    return self._name.partition('/')[0]

  @Pyro4.expose
  def start(self):
    """
    Starts a device.  This should be overridden by inheriting classes.
    """
    pass

  @Pyro4.expose
  def wait(self):
    """
    Waits on device task.  This should be overridden by inheriting classes.
    """
    pass

  @Pyro4.expose
  def stop(self):
    """
    Stops a device.  This should be overridden by inheriting classes.
    """
    pass
