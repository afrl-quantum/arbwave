# vim: ts=2:sw=2:tw=80:nowrap

import logging, re
from logging import log, debug, DEBUG
import ctypes_comedi as clib
from ctypes import cast, pointer, POINTER, c_void_p

from ....tools import cached
from ....tools.path import collect_prefix
from . import subdevice, channels, routes, signal_map


class Card( POINTER(clib.comedi_t) ):
  _type_ = clib.comedi_t

  def _assign(self, other):
    """
    low level assignment of this pointer object.

    This function call should only really be used by the constructor after a
    device has been opened.
    """
    self_ptr = cast( pointer(self), POINTER(c_void_p) )
    other_ptr = cast( pointer(other), POINTER(c_void_p) )
    self_ptr.contents.value = other_ptr.contents.value

  def _zero(self, value=0):
    """
    low level direct assignment of the value of this pointer object.

    This function call should only really be used after comedi_close.
    """
    self_ptr = cast( pointer(self), POINTER(c_void_p) )
    self_ptr.contents.value = value


  @staticmethod
  def get_card_number(device_filename):
    m = re.match('/dev/comedi(?P<board_number>[0-9]+)$', device_filename)
    return None if not m else m.group('board_number')

  def __init__(self, driver, device_file):
    super(Card,self).__init__()

    self.driver = driver
    self.device_file    = device_file
    self.routed_signals = dict()
    self.prefix = '' # shouldn't need this because of defaults in ni_routes

    self._assign( clib.comedi_open(self.device_file) )
    if not self:
      raise NameError('could not open comedi device file: ' + self.device_file)

    self.device = 'Dev'+self.get_card_number(device_file)
    self.route_loader = rl= routes.getRouteLoader(self.kernel) ( driver, self )
    self.sig_map= signal_map.getSignalLoader(self.kernel) (self)

    gus = subdevice.enum.get_useful_subdevices
    self.ao_subdevices      = gus(self, clib.COMEDI_SUBD_AO)
    self.do_subdevices      = gus(self, clib.COMEDI_SUBD_DO)

    self.dio_subdevices     = gus(self, clib.COMEDI_SUBD_DIO)
    self.counter_subdevices = gus(self, clib.COMEDI_SUBD_COUNTER)

    self.subdevices = dict()
    self.subdevices.update( { str(ao):ao for ao in self.ao_subdevices } )
    self.subdevices.update( { str(do):do for do in self.do_subdevices } )
    self.subdevices.update( { str(dio):dio for dio in self.dio_subdevices } )
    self.subdevices.update( { str(co):co for co in self.counter_subdevices } )
    self.signals = [
      channels.Backplane(src,destinations=dest,invertible=True)
      for src,dest in rl.src_to_dst.iteritems()
    ]


    List = gus(self, clib.COMEDI_SUBD_DIO, ret_index_list=True)

    self.backplane_subdevices = dict()

    for dev, index in List:
      sdev = subdevice.Digital(routes.getRouteLoader(dev.kernel) ( driver, dev ), dev, index, name_uses_subdev=False)
      if subdevice.Subdevice.status(sdev)['internal']:
        self.backplane_subdevices[str(sdev)+str(sdev.subdevice)] = sdev

    #Fixed? But not implemented
    # #if self.driver.startswith('ni_'):
    # #  FIXME:  we should not need to use ni_ specifically here.  that should be
    # #  taken care of in RouteLoader
    # #  # for now, we only know how to deal with NI devices (that have the
    # #  # backplane on subdevice 10)
    # #  self.backplane_subdevice = subdevice.Backplane(self, 10, self.prefix)
    # # *** actually, as Ian has found, subdevice=7 is also special as it
    # # represents the PFI I/O lines.



  def set_signals(self, signals):
    '''
    Accesses sig_map to transform arbwave terminal/signal names into appropriate comedi ints
    '''
    if self.routed_signals != signals:
      old = set( self.routed_signals.keys() )
      new = set( signals.keys() )

      # disconnect routes no longer in use
      for route in ( old - new ):
        if 'External/' in route[0] or 'External/' in route[1]:
          continue

        s, d = self.route_loader.route_map[ route ]

        if d.find(str(self).rstrip(str(self.driver)))>-1:
          d = d.lstrip(str(self.driver)+str(self))
          d = self.sig_map.ch_nums(d)
          clib.comedi_dio_config(self, d['subdev'], d['chan'], clib.COMEDI_INPUT) # an attempt to protect the dest terminal

      # connect new routes routes no longer in use
      for route in ( new - old ):
        if 'External/' in route[0] or 'External/' in route[1]:
          continue

        s, d = self.route_loader.route_map[ route ]
        s = s.lstrip(str(self.driver)+str(self))

        if s is None or d is None:
          continue # None means an external connection

        if d.find(str(self).lstrip(str(self.driver)))>-1:
          d_dev = d.lstrip(str(self.driver)+str(self))

          d =  self.sig_map.ch_nums[d_dev]

          if d['kind'] == 'ao_clock':
            AO_CLOCK = {d_dev:self.sig_map.sig_nums_AO_CLOCK[s]}
            return AO_CLOCK
             #Ctr0InternalOutput is listed as routing to the ao clock, but I've found no way to do this.

             #fixed. found separate clock sig_num function. no longer driver dependent.
             ##plus one to reflect ni driver offset? TODO: make this make sense. edit driver?

          if d['kind'] == 'trigger':
            TRIGGER = {d_dev:self.sig_map.sig_nums_EXT[s]}
            return TRIGGER

          if d['kind'] =='PFI':
            s =  self.sig_map.sig_nums_PFI[s]
            clib.comedi_dio_config(self, d['subdev'], d['chan'], clib.COMEDI_OUTPUT)
            clib.comedi_set_routing(self,  d['subdev'], d['chan'], s)
          if d['kind'] =='RTSI':
            s =  self.sig_map.sig_nums_RTSI[s]
            clib.comedi_dio_config(self, d['subdev'], d['chan'], clib.COMEDI_OUTPUT)
            clib.comedi_set_routing(self,  d['subdev'], d['chan'], s)
          #TODO: GPCT config/routing, CDIO clocks?
    self.routed_signals = signals



  def __str__(self):
    return '{}/{}'.format(self.driver, self.device)

  def __del__(self):
    # first instruct each one of the subdevs to be deleted
    # the intent is that this will (for each subdevice):
    #   - cancel all running jobs ( comedi_cancel )
    while self.subdevices:
      subname, subdev = self.subdevices.popitem()
      del subdev

    gus = subdevice.enum.get_useful_subdevices
    List = gus(self, clib.COMEDI_SUBD_DIO, ret_index_list=True)

    for device, index in List:
      chans = clib.comedi_get_n_channels(self, index)
      clib.comedi_dio_config(self, index, chans, clib.COMEDI_INPUT)


    # Fixed?
    # # Set all routes to their default and configure all routable pins to
    # # COMEDI_INPUT as an attempt to protect any pins from damage
    # # Following Ian's work, this means using both "Backplane" type subdevices (7
    # # and 10) to unroute and protect all RTSI/PXI trigger lines and all PFI I/O
    # # lines.
    # # FIXME:  properly close/delete all "Signal" subdevices (like PFI and RTSI)

    # now close the comedi device handle
    clib.comedi_close(self)
    self._zero() # zero the address of this device pointer


  def stop(self):
    # FIXME:  This is BAD!
    self.__del__()

  def start(self):
    print "dev start not implemented"

  @cached.property
  def board(self):
    return clib.comedi_get_board_name(self).lower()

  @cached.property
  def kernel(self):
    return clib.comedi_get_driver_name(self).lower()
