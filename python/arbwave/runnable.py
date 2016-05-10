# vim: ts=2:sw=2:tw=80:nowrap
"""
Defines Runnable class that a user overloads in order to define more complex
operations during a data run.
"""

__all__ = ['Runnable']

class Runnable(object):
  """
  Runnable class to allow more significant complexity during a data run.

  This implementation mostly defines the interface that runnables provide, but
  this is also the implementation of the "Default" runnable that is used to
  execute output in continuous mode.
  """
  def extra_data_labels(self):
    """
    Returns list of names of extra results returned by self.run()
    """
    return list()

  def onstart(self):
    """
    Executed before the runnable is started.
    """
    pass

  def onstop(self):
    """
    Executed after the runnable is stopped.
    """
    pass

  def run(self):
    """
    The body of any inner loop.
    """
    # This implementation is for the Default continuous runnable
    from processor.engine import Arbwave
    Arbwave.instance(new=False).update(continuous=True)
