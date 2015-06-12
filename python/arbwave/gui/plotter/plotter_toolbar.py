# vim: ts=2:sw=2:tw=80:nowrap

from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg

class NavigationToolbar(NavigationToolbar2GTKAgg):
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
        ('HZoom', 'Zoom to horizontal span','zoom_to_rect', 'hspan'),
      )
    if self.vspan_controls:
      toolitems.append(
        ('VZoom', 'Zoom to vertical span','zoom_to_rect', 'vspan'),
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
    NavigationToolbar2GTKAgg.zoom(self,*args)


  def pan(self,*args):
    self.disable_all_span_controls()
    NavigationToolbar2GTKAgg.pan(self,*args)


  def home(self,*args):
    """This version of 'home' resets the history, instead of just clipping it to
    this view"""
    NavigationToolbar2GTKAgg.home(self,*args)
    self.set_max_ranges()
    self.update() # reset the history...


  def hspan(self,*args):
    'Activate the horizontal span selector tool'
    if self._active == 'HSPAN':
      self._active = None
    else:
      self._active = 'HSPAN'

    if self._idPress is not None:
      self._idPress=self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if  self._active:
      self.mode = 'zoom hspan'
      self.canvas.widgetlock(self)
    else:
      self.mode = ''
      self.canvas.widgetlock.release(self)

    for s in self.hspan_controls:
      setattr(s, 'visible', bool(self._active))

    # for simplicity we'll disable the vspan_controls regardless of whether
    # they were in use or not
    for s in self.vspan_controls:
      setattr(s, 'visible', False)

    self.set_message(self.mode)

    # push the current view to define home if stack is empty
    if self._views.empty():
      self.push_current()


  def vspan(self,*args):
    'Activate the vertial span selector tool'
    if self._active == 'VSPAN':
      self._active = None
    else:
      self._active = 'VSPAN'

    if self._idPress is not None:
      self._idPress=self.canvas.mpl_disconnect(self._idPress)
      self.mode = ''

    if self._idRelease is not None:
      self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
      self.mode = ''

    if  self._active:
      self.mode = 'zoom vspan'
      self.canvas.widgetlock(self)
    else:
      self.mode = ''
      self.canvas.widgetlock.release(self)

    for s in self.vspan_controls:
      setattr(s, 'visible', bool(self._active))

    # for simplicity we'll disable the hspan_controls regardless of whether
    # they were in use or not
    for s in self.hspan_controls:
      setattr(s, 'visible', False)

    self.set_message(self.mode)

    # push the current view to define home if stack is empty
    if self._views.empty():
      self.push_current()
