# vim: et:ts=2:sw=2:tw=80:nowrap
#
#       Py_Shell.py : inserts the python prompt in a gtk interface
#

import ipython_view
from gi.repository import Gtk as gtk, \
                          GLib as glib


class Python(ipython_view.IPythonView):
  def __init__(self, get_globals = lambda : dict(),
                     reset = lambda **kw: None,
                     ui = None ):
    config = ipython_view.Config()
    config.TerminalInteractiveShell.autocall = 1
    super(Python,self).__init__(config=config, user_ns=get_globals())
    self.remote_reset = reset
    self.ui = ui
    self._create_shell_cmds()
    self.register_shell_cmds()

  def reset(self, **kwargs):
    glib.idle_add( self.remote_reset, **kwargs )

  def _create_shell_cmds(self):
    def reset( **kwargs ):
      """
      Rerun global script.

      Each of the keyword arguments will be passed into the global script in the
      global variable 'kwargs' (a python dictionary).
      """
      self.reset(**kwargs)

    def quit():
      gtk.main_quit()

    self.shell_cmds = [ reset, quit ]

    if self.ui:
      def save():
        """
        Save the configuration file.
        """
        self.ui.save()

      def saveas(target, keep=True):
        """
        target : target filename to save to
        keep   : whether to keep the current config filename after saving
                 [Default True]
        """
        old = self.ui.config_file
        self.ui.config_file = target
        try:
          self.ui.save()
        finally:
          self.ui.config_file = old

      self.shell_cmds += [ save, saveas ]

  def register_shell_cmds(self):
      self.updateNamespace({ f.func_name:f for f in self.shell_cmds })

  def update_globals(self, G=None):
    """
    The user globals (user_ns) have been cleared and reinitialized.  We need to
    add back in the ipython stuff as well as any local shell commands.
    """
    self.IP.init_user_ns()
    self.register_shell_cmds() # second so it overrides ipython 'quit'



if __name__ == "__main__":
  window = gtk.Window()
  window.set_default_size(640, 320)
  window.connect('delete-event', lambda x, y: gtk.main_quit())
  sb = gtk.ScrolledWindow()
  sb.add(Python())
  window.add( sb )
  window.show_all()
  gtk.main()
