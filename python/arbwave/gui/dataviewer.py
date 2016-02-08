#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
import sys

if __name__ == '__main__':
  from os.path import join as path_join, dirname, pardir
  sys.path.insert(0, path_join( dirname(__file__), pardir, pardir ) )
  if sys.platform != 'win32':
    # this will change for the distant future of python3 with arbwave
    import billiard as mp
    mp.set_start_method('spawn')
  import arbwave.gui.dataviewer
  arbwave.gui.dataviewer.main()
  sys.exit()


def main():
  dv = DataViewer()
  dv.show()
  dv.disable_reuse()
  dv.join()


if sys.platform == 'win32':
  # windows already normally uses spawn instead of fork
  import multiprocessing as mp
else:
  # We are currently using billiard on non-windows systems because the
  # multiprocessing library in python2.7 is not good for gtk--in only forks and
  # does not spawn-->causes many memory collisions with gtk internal pipes.
  # When we move to python3 some far future day (or when
  # multiprocessing.set_start_method is backported to python2), we'll use the
  # builtin module instead of billiard.
  import billiard as mp



class DataViewer(mp.Process):
  CLIENT = 0
  SERVER = 1
  def __init__(self, *args, **kwargs):
    super(DataViewer,self).__init__()
    self.q      = mp.Queue()
    self.cmds   = mp.Pipe()
    self.args   = args
    self.kwargs = kwargs
    self.daemon = True

  def __del__(self):
    if self.q is not None:
      self.terminate()
      self.join()
      self.q.close()
      self.cmds[self.CLIENT].close()
      self.cmds[self.SERVER].close()
      del self.q, self.cmds
      self.q = self.cmds = None

  def show(self):
    # we'll only start if we haven't started before
    if not self.is_alive():
      self.start()

  def run(self):
    from gi.repository import Gtk as gtk, GObject as gobject
    from .datadialog import DataDialog

    # This necessarily runs in a new process
    gobject.timeout_add(100, self.deque)
    self.viewer = DataDialog(*self.args, **self.kwargs)
    self.viewer.show_all()
    gtk.main()

  def add(self, *stuff):
    """
    Push items to the queue to plot.  This function generally runs in the
    arbwave process.
    """
    self.q.put(stuff)

  @property
  def reusable(self):
    if not self.is_alive(): return False
    self.cmds[self.CLIENT].send('get_reuse')
    return self.cmds[self.CLIENT].recv()

  @reusable.setter
  def reusable(self, value):
    if not self.is_alive():
      raise RuntimeError('not running')
    self.cmds[self.CLIENT].send('set_reuse')
    self.cmds[self.CLIENT].send(value)

  def disable_reuse(self):
    if not self.is_alive(): return
    self.cmds[self.CLIENT].send('disable_reuse')

  def _cmd_response(self):
    """
    respond to commands sent to us by the parent process.
    """
    if not self.cmds[self.SERVER].poll():
      return
    cmd = self.cmds[self.SERVER].recv()

    if    cmd == 'get_reuse':
      self.cmds[self.SERVER].send( self.viewer.reuse.get_active() )
    elif  cmd == 'set_reuse':
      value = self.cmds[self.SERVER].recv()
      self.viewer.reuse.set_active(value)
    elif  cmd == 'disable_reuse':
      self.viewer.reuse.set_active(False)
      self.viewer.reuse.set_sensitive(False)

  def deque(self):
    """
    Pop items off the queue to plot.  self.run sets this up in timed gtk loop.
    """
    if not self.is_alive():
      return False

    self._cmd_response() # first start off with cmds:
    try:
      stuff = self.q.get_nowait()
    except mp.queues.Empty:
      pass
    else:
      self.viewer.add( *stuff )
    return True


class ViewerDB:
  def __init__(self):
    self.db = dict()

  def get(self, columns, title=None):
    key = ( tuple(columns), title )
    if key in self.db:
      s = self.db[key]
      if s.reusable:
        return s
      else:
        s.disable_reuse()
        self.db.pop(key)

    s = DataViewer(columns=columns, title=title)
    self.db[key] = s
    return s

db = ViewerDB()
