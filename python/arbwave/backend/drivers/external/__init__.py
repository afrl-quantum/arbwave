# vim: ts=2:sw=2:tw=80:nowrap

import logging
import re
from ...driver import Driver as Base
from channels import Timing, Backplane


class Driver(Base):
  prefix      = 'External'
  description = 'External Hardware'
  has_simulated_mode = True

  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)
    # hook the simulated library if needed

    self.clocks = dict()
    self.routed_signals = dict()

  def start(self):
    """Dummy start function because we use this class as the device arg for
    Timing(...)"""
    pass

  def wait(self):
    """Dummy wait function because we use this class as the device arg for
    Timing(...)"""
    pass

  def stop(self):
    """Dummy stop function because we use this class as the device arg for
    Timing(...)"""
    pass

  def get_timing_channels(self):
    retval = [ Timing(clk, self) for clk in self.clocks ]

    # now we add just one more (new) timing channel for the user to add
    for i in xrange(10000):
      clk = 'External/clk{}'.format(i)
      if clk not in self.clocks:
        retval.append( Timing(clk, self) )
        break
    return retval

  def get_routeable_backplane_signals(self):
    return [ #Backplane('External/',['External/'])] + [
      #Backplane(clk_i,['External/']) for clk_i in self.clocks
    ]

  def set_clocks( self, clocks ):
    logging.debug( 'set clocks: %s', clocks )
    self.clocks = clocks.copy()

  def set_signals( self, signals ):
    if self.routed_signals != signals:
      old = set( self.routed_signals.keys() )
      new = set( signals.keys() )

      # disconnect routes no longer in use
      for route in ( old - new ):
        logging.debug( 'ext: disconnect %s-->%s', *route )

      # connect new routes
      for route in ( new - old ):
        logging.debug( 'ext: connect %s-->%s', *route )

      self.routed_signals = signals
