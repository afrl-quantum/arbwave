# vim: ts=2:sw=2:tw=80:nowrap

import re, glob, traceback
from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog
import Pyro4

from ....tools.path import collect_prefix
from ...driver import Driver as Base
from .card import Card
from . import channels


class Driver(Base):
  prefix = 'comedi'
  description = 'Comedi Driver'
  has_simulated_mode = True

  @staticmethod
  def glob_comedi_device_files():
    """creates a list of all comedi device files"""
    pat0, pat1 = '/dev/comedi*', '/dev/comedi[0-9]*$'
    L = [ p for p in glob.glob(pat0) if re.match(pat1, p)]
    L.sort()
    return L


  def __init__(self, *a, **kw):
    super(Driver,self).__init__(*a, **kw)
    # hook the simulated library if needed
    if self.simulated:
      # rehook comedi lib so that hardware is simulated:
      from . import sim
      self.csim = sim.ComediSim()
      self.glob_comedi_device_files = self.csim.glob_device_files


    # device path --> Device instance
    self.cards      = dict()
    self.subdevices = dict()
    self.outputs    = list()
    self.counters   = list()
    self.signals    = list()
    src_dests       = dict()


    for df in self.glob_comedi_device_files():
      if Card.get_card_number( df ) is None:
        continue # don't match subdevices
      try:
        card = Card( self, df )
      except:
        traceback.print_exc()
        print('Could not open comedi card: ', df)
        continue
      self.cards[ str(card) ] = card
      self.subdevices.update( card.subdevices )
      self.outputs  += [ ao for sub in card.ao_subdevices for ao in sub.available_channels ]
      self.outputs  += [ do for sub in card.do_subdevices for do in sub.available_channels ]
      self.outputs  += [ do for sub in card.dio_subdevices for do in sub.available_channels ]
      self.counters += [ sub for sub in card.counter_subdevices  ] #don't collect counter channels
      # aggregate this cards available routes into the complete dictionary
      for src,dest in card.available_routes:
        src_dests.setdefault(src, list()).append(dest)


    # add all the counters as timing sources
    self.timing_channels = [
      channels.Timing(str(ctr), ctr) for ctr in self.counters
    ]

    # add all the onboardclocks that are available
    self.timing_channels += [
      channels.OnboardClock(subd.onboardclock_name, subd)
      for subd in self.subdevices.values() if subd.has_onboardclock
    ]

    # FIXME:  add in DOTiming channels

    # convert the aggregate routes dictionary to a list of Backplane signals
    for src, dests in src_dests.items():
      log(DEBUG-1, 'creating comedi backplane channel: %s --> %s', src, dests)
      self.signals.append(
        channels.Backplane(src,destinations=dests,invertible=False)
      )

    info('found %d comedi supported boards',len(self.cards))

  @Pyro4.expose
  def close(self):
    """
    Close each card.  Each card will first close each of its subdevices.
    """
    while self.cards:
      cardname, card = self.cards.popitem()
      debug( 'closing comedi card: %s', cardname )
      del card

    # clean up the simulated library if necessary
    if self.simulated:
      self.csim.remove_from_clib()

  @Pyro4.expose
  def get_devices(self):
    """
    Return the arbwave notion of devices.  In comedi nomenclature, this
    corresponds to subdevices.
    """
    return self.subdevices.values()

  @Pyro4.expose
  def get_output_channels(self):
    return self.outputs

  @Pyro4.expose
  def get_timing_channels(self):
    return self.timing_channels

  @Pyro4.expose
  def get_routeable_backplane_signals(self):
    return self.signals

  @Pyro4.expose
  def set_device_config( self, config, channels, signal_graph ):
    debug('comedi.set_device_config')
    chans = { k:dict() for k in config }

    # separate channels into subdevice groups.  We cannot use collect_prefix
    # because some of the subdevice channel names have an extra slash.
    for c, ci in channels.items():
      for d in self.subdevices:
        if c.startswith( d ):
          chans[d][c] = ci

    for d, sdev in self.subdevices.items():
      if d in config or d in chans:
        sdev.set_config( config.get(d,{}), chans.get(d,[]), signal_graph )

  @Pyro4.expose
  def set_clocks( self, clocks ):
    # FIXME:  look at new version of this in nidaqmx
    debug('comedi.set_clocks')
    clocks = collect_prefix(clocks, 0, 2, 2)
    for d, sdev in self.subdevices.items():
      if d in clocks:
        sdev.set_clocks( clocks[d] )

  @Pyro4.expose
  def set_signals( self, signals ):
    debug('comedi.set_signals(signals=%s)', signals)
    C = collect_prefix( signals, prefix_len=2, prefix_list=self.cards.keys() )
    for d, dev in self.cards.items():
      dev.set_signals( C.get(d,{}) )

  @Pyro4.expose
  def set_static( self, analog, digital ):
    debug('comedi.set_static')

    # separate channels into subdevice groups.  We cannot use collect_prefix
    # because some of the subdevice channel names have an extra slash.
    sdev_data = dict()
    for c, data in dict( analog, **digital ).items():
      for d in self.subdevices:
        if c.startswith( d ):
          sdev_data.setdefault( d, dict() )
          sdev_data[d][c] = data

    for d, sdev in self.subdevices.items():
      if d in sdev_data:
        sdev.set_output( sdev_data[d] )

  @Pyro4.expose
  def set_waveforms( self, analog, digital, transitions, t_max, continuous ):
    debug('comedi.set_waveforms')

    # separate channels into subdevice groups.  We cannot use collect_prefix
    # because some of the subdevice channel names have an extra slash.
    sdev_data = dict()
    for c, data in dict( analog, **digital ).items():
      for d in self.subdevices:
        if c.startswith( d ):
          sdev_data.setdefault( d, dict() )
          sdev_data[d][c] = data

    for d, sdev in self.subdevices.items():
      if d in sdev_data:
        sdev.set_waveforms( sdev_data[d], transitions, t_max, continuous )
