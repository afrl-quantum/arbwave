# vim: ts=2:sw=2:tw=80:nowrap

from ..gui_callbacks import do_gui_operation

def plot_stuff( plotter, analog, digital, transitions ):
  t_final = 0.0
  if transitions:
    t_final = max(transitions)
  if analog or digital:
    plotter.start()
  if analog:
    plotter.plot_analog( analog, t_final=t_final )
  if digital:
    plotter.plot_digital( digital, t_final=t_final )
  if analog or digital:
    plotter.finish(t_final=t_final)

def to_plotter( plotter, analog, digital, transitions ):
  do_gui_operation( plot_stuff, plotter, analog, digital, transitions )
