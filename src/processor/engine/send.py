# vim: ts=2:sw=2:tw=80:nowrap

from ..gui_callbacks import do_gui_operation

def plot_stuff( plotter, analog, digital ):
  print 'trying to plot stuff...'

def to_plotter( plotter, analog, digital ):
  do_gui_operation( plot_stuff, plotter, analog, digital )
