# vim: ts=2:sw=2:tw=80:nowrap

from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as _NavigationToolbar

from os import path

THIS_DIR = path.dirname( __file__ )

# this is a bit of a hack, since path.join gtk3 backend stuff will not actually
# overwrite this path (since this one is already absolute)
horiz_zoom_to_rect = path.abspath( path.join(THIS_DIR, 'icons', 'horiz_zoom_to_rect') )
vert_zoom_to_rect = path.abspath( path.join(THIS_DIR, 'icons', 'vert_zoom_to_rect') )

class NavigationToolbar(_NavigationToolbar):
  def __init__( self, canvas, window,
                hspan_controls=None,
                vspan_controls=None,
                set_max_ranges=lambda:None ):
    self.hspan_controls = hspan_controls
    self.vspan_controls = vspan_controls
    self.set_max_ranges = set_max_ranges
    toolitems = [
      ('Home', 'Reset original view', 'home', 'home'),
      ('Back', 'Back to  previous view','back', 'back'),
      ('Forward', 'Forward to next view','forward', 'forward'),
      (None, None, None, None),
      ('Pan', 'Pan axes with left mouse, zoom with right', 'move','pan'),
      ('Zoom', 'Zoom to rectangle','zoom_to_rect', 'zoom'),
    ]
    if self.hspan_controls or self.vspan_controls:
      toolitems.append( (None, None, None, None) )
    if self.hspan_controls:
      toolitems.append(
        ('HZoom', 'Zoom to horizontal span',horiz_zoom_to_rect, 'hspan'),
      )
    if self.vspan_controls:
      toolitems.append(
        ('VZoom', 'Zoom to vertical span',vert_zoom_to_rect, 'vspan'),
      )

    toolitems += [
      (None, None, None, None),
      #('Subplots', 'Configure subplots','subplots', 'configure_subplots'),
      ('Save', 'Save the figure','filesave', 'save_figure'),
    ]

    self.toolitems = tuple( toolitems )

    super(NavigationToolbar,self).__init__(canvas, window)



  def disable_all_span_controls(self):
    for s in self.hspan_controls:
      setattr(s, 'visible', False)
    for s in self.vspan_controls:
      setattr(s, 'visible', False)


  def zoom(self,*args):
    self.disable_all_span_controls()
    _NavigationToolbar.zoom(self,*args)


  def pan(self,*args):
    self.disable_all_span_controls()
    _NavigationToolbar.pan(self,*args)


  def home(self,*args):
    """This version of 'home' resets the history, instead of just clipping it to
    this view"""
    _NavigationToolbar.home(self,*args)
    self.set_max_ranges()
    self.update() # reset the history...


  def hspan(self,*args):
    'Activate the horizontal span selector tool'
    if self._active == 'HSPAN':
      self._active = None
    else:
      self._active = 'HSPAN'

    if self.canvas.widgetlock.locked():
      self.canvas.widgetlock.release(self)

    if self._idPress is not None:
      self._idPress=self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if  self._active:
      self.mode = 'zoom hspan'
    else:
      self.mode = ''

    for s in self.hspan_controls:
      setattr(s, 'visible', self._active == 'HSPAN')

    # for simplicity we'll disable the vspan_controls regardless of whether
    # they were in use or not
    for s in self.vspan_controls:
      setattr(s, 'visible', False)

    self.set_message(self.mode)

    # push the current view to define home if stack is empty
    if self._nav_stack.empty():
      self.push_current()


  def vspan(self,*args):
    'Activate the vertial span selector tool'
    if self._active == 'VSPAN':
      self._active = None
    else:
      self._active = 'VSPAN'

    if self.canvas.widgetlock.locked():
      self.canvas.widgetlock.release(self)

    if self._idPress is not None:
      self._idPress=self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if  self._active:
      self.mode = 'zoom vspan'
    else:
      self.mode = ''

    for s in self.vspan_controls:
      setattr(s, 'visible', self._active == 'VSPAN')

    # for simplicity we'll disable the hspan_controls regardless of whether
    # they were in use or not
    for s in self.hspan_controls:
      setattr(s, 'visible', False)

    self.set_message(self.mode)

    # push the current view to define home if stack is empty
    if self._nav_stack.empty():
      self.push_current()
