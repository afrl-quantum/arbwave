# vim: ts=2:sw=2:tw=80:nowrap

import re, glob, traceback
from logging import info, error, warn, debug, log, DEBUG, INFO, root as rootlog

from ....tools.path import collect_prefix
from ...driver import Driver as Base
from .card import Card


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
      import sim # rehook comedi lib so that hardware is simulated.
      self.csim = sim.ComediSim()
      self.glob_comedi_device_files = self.csim.glob_device_files


    # device path --> Device instance
    self.cards      = dict()
    self.subdevices = dict()
    self.analogs    = list()
    self.lines      = list()
    self.counters   = list()
    self.signals    = list()


    for df in self.glob_comedi_device_files():
      if Card.get_card_number( df ) is None:
        continue # don't match subdevices
      try:
        card = Card( self, df )
      except:
        traceback.print_exc()
        print 'Could not open comedi card: ', df
        continue
      self.cards[ str(card) ] = card
      self.subdevices.update( card.subdevices )
      self.analogs  += [ ao for sub in card.ao_subdevices for ao in sub.available_channels ]
      self.lines    += [ do for sub in card.do_subdevices for do in sub.available_channels ]
      self.lines    += [ do for sub in card.dio_subdevices for do in sub.available_channels ]
      self.counters += [ sub for sub in card.counter_subdevices  ] #don't collect counter channels
      self.signals  += [ so for  so in card.signals ]

    info('found %d comedi supported boards',len(self.cards))



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

  def get_devices(self):
    """
    Return the arbwave notion of devices.  In comedi nomenclature, this
    corresponds to subdevices.
    """
    return self.subdevices.values()

  def get_analog_channels(self):
    return self.analogs

  def get_digital_channels(self):
    return self.lines

  def get_timing_channels(self):
    # FIXME:  add in DOTiming channels
    return self.counters

  def get_routeable_backplane_signals(self):
    return self.signals


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


  def set_clocks( self, clocks ):
    # FIXME:  look at new version of this in nidaqmx
    debug('comedi.set_clocks')
    clocks = collect_prefix(clocks, 0, 2, 2)
    for d, sdev in self.subdevices.items():
      if d in clocks:
        sdev.set_clocks( clocks[d] )


  def set_signals( self, signals ):
    debug('comedi.set_signals(signals=%s)', signals)
    C = collect_prefix( signals, prefix_len=2, prefix_list=self.cards.keys() )
    for d, dev in self.cards.items():
      dev.set_signals( C.get(d,{}) )




  def set_static( self, analog, digital ):
    debug('comedi.set_static')

    # separate channels into subdevice groups.  We cannot use collect_prefix
    # because some of the subdevice channel names have an extra slash.
    sdev_data = dict()
    for c, data in dict( analog, **digital ).viewitems():
      for d in self.subdevices:
        if c.startswith( d ):
          sdev_data.setdefault( d, dict() )
          sdev_data[d][c] = data

    for d, sdev in self.subdevices.items():
      if d in sdev_data:
        sdev.set_output( sdev_data[d] )

  def set_waveforms( self, analog, digital, transitions, t_max, continuous ):
    debug('comedi.set_waveforms')

    # separate channels into subdevice groups.  We cannot use collect_prefix
    # because some of the subdevice channel names have an extra slash.
    sdev_data = dict()
    for c, data in dict( analog, **digital ).viewitems():
      for d in self.subdevices:
        if c.startswith( d ):
          sdev_data.setdefault( d, dict() )
          sdev_data[d][c] = data

    for d, sdev in self.subdevices.items():
      if d in sdev_data:
        sdev.set_waveforms( sdev_data[d], transitions, t_max, continuous )
