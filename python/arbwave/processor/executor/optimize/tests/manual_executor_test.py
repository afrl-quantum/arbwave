# vim: ts=2:sw=2:tw=80:nowrap

from gi.repository import Gtk as gtk
from numpy.random import rand

var0 = 0.4
var1 = 30
var2 = dict( a = 100, b = 2000 )

nan = float('nan')

class func:
  def __init__(self, avg=False, Nextra=8):
    self.avg = avg
    self.ne = Nextra

  def onstart(self):
    print('nothing to get ready for!')

  def onstop(self):
    print('nothing to clean up!')

  def run(self):
    global var0, var1, var2
    xx = var0 * 100
    yy = var1 * 1
    zz0 = var2['a'] * 0.01
    zz1 = var2['b'] * 0.0001
    #f = ( sin((xx/40. + (yy/30.)**2))**2.0) * 100.0
    f = xx**2 + abs(yy-100) * abs(yy+100) + abs(zz0-100) + (zz1+50)**2
    R = list(rand(self.ne))
    if self.avg:
      #return average([ f for i in range(10) ])
      return [average([ poisson( f ) for i in range(10) ])] + R
    else:
      return [f] + R

  def extra_data_labels(self):
    return ['rand'] * self.ne


def get_globals():
  return globals()

import traceback, pprint
from ..executor import Make

main_settings = dict()

def main():
  win = gtk.Window()
  e = Make(win, 'func', main_settings)( func(), globals() )

  print('e: ', e)
  return e
  try:
    while e(): pass
  except: traceback.print_exc()
  if e.results:
    print('cache length: ', len(e.results))
    print('skipped evals: ', e.skipped_evals)
    #print('results: ')
    #pprint.pprint( e.results )
