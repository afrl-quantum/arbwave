# vim: ts=2:sw=2:tw=80:nowrap

import logging, re
from logging import log, debug, DEBUG
import comedi
from ctypes import cast, pointer, POINTER, c_void_p

from ....tools import cached
from ....tools.path import collect_prefix
from . import subdevice, channels, names


class Card( POINTER(comedi.comedi_t) ):
  _type_ = comedi.comedi_t

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

    This function call should only really be used after comedi.close.
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

    self._assign( comedi.open(self.device_file) )
    if not self:
      raise NameError('could not open comedi device file: ' + self.device_file)

    self.device = 'Dev'+self.get_card_number(device_file)

    gus = subdevice.enum.get_useful_subdevices
    self.ao_subdevices      = gus(self, comedi.SUBD_AO)
    self.do_subdevices      = gus(self, comedi.SUBD_DO)

    self.dio_subdevices     = gus(self, comedi.SUBD_DIO)
    self.counter_subdevices = gus(self, comedi.SUBD_COUNTER)

    self.subdevices = dict()
    self.subdevices.update( { str(ao):ao for ao in self.ao_subdevices } )
    self.subdevices.update( { str(do):do for do in self.do_subdevices } )
    self.subdevices.update( { str(dio):dio for dio in self.dio_subdevices } )
    self.subdevices.update( { str(co):co for co in self.counter_subdevices } )


    #List = gus(self, comedi.SUBD_DIO, ret_index_list=True)
    #self.backplane_subdevices = dict()
    #for dev, index in List:
    #  sdev = subdevice.Digital(routes.getRouteLoader(dev.kernel) ( driver, dev ), dev, index, name_uses_subdev=False)
    #  if subdevice.Subdevice.status(sdev)['internal']:
    #    self.backplane_subdevices[str(sdev)+str(sdev.subdevice)] = sdev

  @cached.property
  def signal_names(self):
    return names.get_signal_names(self.kernel, self.driver.host_prefix, str(self))

  @cached.property
  def name_table(self):
    return {v['arbwave']:k for k,v in self.signal_names['signals'].items()}

  @cached.property
  def available_routes(self):
    # first generate all external-cable routes
    D = self.signal_names['signals']
    R = list()
    for n in D.values():
      if n['external_in']:
        R.append(('External/', n['arbwave']))
      if n['external_out']:
        R.append((n['arbwave'], 'External/'))

    # next, collect names of all routes that do not involve external cables
    count = comedi.get_routes(self, None, 0)
    pairs = (comedi.route_pair * count)()
    comedi.get_routes(self, pairs, count)
    R += [(D[r.source]['arbwave'],D[r.destination]['arbwave']) for r in pairs]
    return R


  nlkup = lambda self, *a: [self.name_table[i] for i in a]


  def set_signals(self, signals):
    '''
    Comedi signal router.

    Uses new interface to route signals.
    '''
    if self.routed_signals != signals:
      debug('comedi.card(%s).set_signals(signals=%s)', self, signals)

      old = set( self.routed_signals.keys() )
      new = set( signals.keys() )

      # disconnect routes no longer in use
      ext_len = len('External/')
      for route in ( old - new ):
        if 'External/' in [route[0][:ext_len], route[1][:ext_len]]:
          continue
        if comedi.disconnect_route(self, *self.nlkup(*route)):
          raise OSError('comedi: Could not unroute signal {}-->{}'.format(*route))

      # connect new routes routes
      for route in ( new - old ):
        if 'External/' in [route[0][:ext_len], route[1][:ext_len]]:
          continue

        if None in route:
          continue # None means an incomplete connection(?)
        if comedi.connect_route(self, *self.nlkup(*route)):
          raise OSError('comedi: Could not route signal {}-->{}'.format(*route))

    self.routed_signals = signals



  def __str__(self):
    return '{}/{}'.format(self.driver, self.device)

  def close(self):
    # first instruct each one of the subdevs to be deleted
    # the intent is that this will (for each subdevice):
    #   - cancel all running jobs ( comedi.cancel )
    while self.subdevices:
      subname, subdev = self.subdevices.popitem()
      subdev.clear()
      del subdev

    List = subdevice.enum.get_useful_subdev_list(self, comedi.SUBD_DIO)

    for index in List:
      chans = comedi.get_n_channels(self, index)
      for ch in range(chans):
        comedi.dio_config(self, index, ch, comedi.INPUT)


    # Fixed?
    # # Set all routes to their default and configure all routable pins to
    # # COMEDI_INPUT as an attempt to protect any pins from damage
    # # Following Ian's work, this means using both "Backplane" type subdevices (7
    # # and 10) to unroute and protect all RTSI/PXI trigger lines and all PFI I/O
    # # lines.
    # # FIXME:  properly close/delete all "Signal" subdevices (like PFI and RTSI)

    # now close the comedi device handle
    comedi.close(self)
    self._zero() # zero the address of this device pointer

  def stop(self):
    # FIXME:  This is BAD!
    self.close()

  def start(self):
    print("dev start not implemented")

  @cached.property
  def board(self):
    return str(comedi.get_board_name(self)).lower()

  @cached.property
  def kernel(self):
    return str(comedi.get_driver_name(self)).lower()
