# vim: ts=2:sw=2:tw=80:nowrap

import re, glob, traceback
from logging import error, warn, debug, log, DEBUG, INFO, root as rootlog

from ....tools.path import collect_prefix
from ...driver import Driver as Base
from .card import Card


class Driver(Base):
  prefix = 'comedi'
  description = 'Comedi Driver'
  has_simulated_mode = False # will not be a lie some time in the future

  @staticmethod
  def glob_comedi_device_files():
    """creates a list of all comedi device files"""
    return glob.glob('/dev/comedi*')


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

    print 'found {} comedi supported boards'.format(len(self.cards))



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


  def set_device_config( self, config, channels, shortest_paths ):
    # FIXME:  This looks like it needs a bit of help
    debug('comedi.set_device_config')
    subdev_chans = dict()
    chans = dict()

    for s in self.subdevices.keys():
        subdev_pre = re.search('(\w*/\w*/\D*)', s)
        for c in channels:
          chan_pre = re.search('(\w*/\w*/\w*)', c) #could be more specific
          if subdev_pre.group() == chan_pre.group():
            subdev_chans.update( {c:channels[c]} )
            chans.update( {s:subdev_chans} )

    for d, sdev in self.subdevices.items():
      if d in config or d in chans:
        cheat = re.search('(\w*/\w*/\D*)', d) ## this is a cheating fix for mismatched subdevice naming conventions
        sdev.set_config( config.get(cheat.group(),{}), chans.get(d,[]), shortest_paths )


  def set_clocks( self, clocks ):
    # FIXME:  look at new version of this in nidaqmx
    debug('comedi.set_clocks')
    clocks = collect_prefix(clocks, 0, 2, 2)
    for d, sdev in self.subdevices.items():
      if d in clocks:
        sdev.set_clocks( clocks[d] )


  def set_signals( self, signals ):
    debug('comedi.set_signals')
    for d, dev in self.cards.items():
      dev.Sigconfig(signals)




  def set_static( self, analog, digital ):
    debug('comedi.set_static')
    D = collect_prefix(digital, 0, 2, 2)
    A = collect_prefix(analog, 0, 2, 2)

    #selects all valid subdevices insead of arbitrary choice
    #later we may want to select from available subdevices
    for dev, data in D.items():
      for i in self.subdevices.keys():
        sdev = re.search(dev+"(/do[0-9]*)", i)
        if sdev:
          self.subdevices[ sdev.group() ].set_output( data )

    for dev, data in A.items():
      for i in self.subdevices.keys():
        sdev = re.search(dev+"(/ao[0-9]*)", i)
        if sdev:
          self.subdevices[ sdev.group() ].set_output( data )

  def set_waveforms( self, analog, digital, transitions, t_max, continuous ):
    debug('comedi.set_waveforms')

    D = collect_prefix( digital, 0, 2, 2 )
    A = collect_prefix( analog, 0, 2, 2 )
    C = collect_prefix( transitions, 0, 2, 2)

    #TO DO: select all valid subdevices as above.
    for d,sdev in self.subdevices.items():
      if d in D or d in C:
        sdev.set_waveforms( D.get(d,{}), C.get(d,{}), t_max, continuous )

    for dev in A.items():
      self.subdevices[ dev[0]+'/ao1' ].set_waveforms( dev[1], transitions, t_max, continuous )
