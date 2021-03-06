#!/usr/bin/env python3
# vim: ts=2:sw=2:tw=80:nowrap
import sys

if __name__ == '__main__':
  from os.path import join as path_join, dirname, pardir
  sys.path.insert(0, path_join( dirname(__file__), pardir, pardir ) )
  if sys.platform != 'win32':
    # this will change for the distant future of python3 with arbwave
    import multiprocessing as mp
    mp.set_start_method('spawn')
  import arbwave.gui.dataviewer
  arbwave.gui.dataviewer.main()
  sys.exit()


def main():
  dv = DataViewer()
  dv.show()
  dv.disable_reuse()
  dv.join()


import multiprocessing as mp



class DataViewer(mp.Process):
  CLIENT = 0
  SERVER = 1
  tweaks = dict()

  @classmethod
  def set_tweaks(cls, **kw):
    """
    Tweak aspects of the DataViewer by passing in keyword arguments:
      fmt      :
        A single string to specify the formatting of all data columns
        *or* a sequence of strings that specify the formatting of each data
        column individually.
        Note!!:  If a sequence is given, a string must be given for every data
        column.
      autonamer:
        function to change the naming of files when new files are saved.  This
        function should return a dictionary with any one of the following
        keywords:
          filters     : to set the values of the file-extention filters.
                        Example:  filters=[('*.dat', 'Data Files (*.dat)')]
          default_dir : Override the default directory in which to open (rather
                        than just using the last directory selected).
          default_filename : Suggest a default filename in the filechooser
                        dialog.
    """
    cls.tweaks = kw

  def __init__(self, *args, **kwargs):
    super(DataViewer,self).__init__()
    self.q      = mp.Queue()
    self.cmds   = mp.Pipe()
    self.args   = args
    self.kwargs = dict(self.tweaks, **kwargs)
    self.daemon = True

  #Not sure what this really was for
  #def __del__(self):
  #  if self.q is not None:
  #    self.terminate()
  #    self.join()
  #    self.q.close()
  #    self.cmds[self.CLIENT].close()
  #    self.cmds[self.SERVER].close()
  #    del self.q, self.cmds
  #    self.q = self.cmds = None

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
    key = ( columns, title )
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
