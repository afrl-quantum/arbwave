# vim: ts=2:sw=2:tw=80:nowrap
import gtk, gobject

class Notification(gtk.Window):
  def __init__( self, fade_dt=6, get_position=None,
                parent=None, type=gtk.WINDOW_POPUP, *args, **kwargs):
    gtk.Window.__init__(self, type, *args, **kwargs)

    self.pause_fadeout = False
    self.fade_time0 = None
    self.fade_dt = fade_dt
    self.my_get_position = get_position
    if self.my_get_position:
      assert callable(self.my_get_position), \
        'notification positioner must be callable'

    if parent:
      self.set_transient_for( parent )
      self.set_destroy_with_parent(True)

    self.set_urgency_hint(True)
    self.set_type_hint( gtk.gdk.WINDOW_TYPE_HINT_TOOLTIP )
    self.set_app_paintable(True)
    self.set_resizable(False)
    self.set_name('gtk-tooltip')

    style = self.get_style()

    a = gtk.Alignment(0.5,0.5,1.0,1.0)
    a.set_padding( style.ythickness,
                   style.ythickness,
                   style.xthickness,
                   style.xthickness )
    self.add( a )
    a.show()
    b = gtk.HBox( False, style.xthickness )
    a.add( b )
    b.show()
    self.image = gtk.Image()
    b.pack_start( self.image, False, False, 0 )
    self.label = gtk.Label('Help! Help! Let me outa here!')
    self.label.set_line_wrap( True )
    b.pack_start(self.label, False, False, 0)
    a.set_padding( 10*style.ythickness,
                   10*style.ythickness,
                   10*style.xthickness,
                   10*style.xthickness )
    b.set_spacing( 10*style.xthickness )
    # style.paint_flat_box(
    #   self.window,
    #   gtk.STATE_NORMAL,
    #   gtk.SHADOW_OUT,
    #   None, self, 'tooltip', 0, 0,
    #   self.allocation.width,
    #   self.allocation.height )
    # self.is_composited()
    # import cairo

    self.connect( 'enter-notify-event', lambda w,e: self.set_fade_pause(True) )
    self.connect( 'leave-notify-event', lambda w,e: self.set_fade_pause(False) )

  def set_fade_pause(self, V):
    self.pause_fadeout = V

  def _reset_t0(self):
    self.fade_time0 = gobject.get_current_time()

  def dim(self):
    if self.pause_fadeout:
      if self.is_composited():
        self.set_opacity(1)
      self._reset_t0()
      return True

    t = gobject.get_current_time()
    opacity = 1.0 - ((t-self.fade_time0)/self.fade_dt)**3.0
    if opacity <= 0.0:
      self.hide()
      return False

    if self.is_composited():
      self.set_opacity( opacity )
    return True

  def show(self, markup):
    self.label.set_markup(markup)
    self.label.show()
    self.image.hide()
    if self.my_get_position:
      pos = self.my_get_position()
      sz = self.get_size()
      self.move( int(pos[0]-sz[0]*.5), (pos[1]-sz[1]) )
    self.present()

    if self.is_composited():
      self.set_opacity(1)
    self._reset_t0()
    gobject.timeout_add( 100, self.dim )

if __name__ == '__main__':
  n = Notification(get_position=lambda : (300,200))
  n.show('<span fgcolor="red"><b>Error:</b>  You must like errors!</span>')
  
  import time
  gtk.main()
