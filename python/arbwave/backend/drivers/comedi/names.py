# vim: ts=2:sw=2:tw=80:nowrap
"""
Converts signal/terminal constants to names specific to a particular device
driver.
"""

from logging import debug
import re
import comedi

ni_macros = (
  # comedi name             arbwave name                      Ext connection
  ('NI_PFI',                '{dev}/PFI({i})',                 True),
  ('TRIGGER_LINE',          '{host}TRIG/{i}',                 False),
  ('NI_RTSI_BRD',           '{dev}/RTSI_BRD({i})',            False),
  ('NI_CtrSource',          '{dev}/CtrSource({i})',           False),
  ('NI_CtrGate',            '{dev}/CtrGate({i})',             False),
  ('NI_CtrAux',             '{dev}/CtrAux({i})',              False),
  ('NI_CtrA',               '{dev}/CtrA({i})',                False),
  ('NI_CtrB',               '{dev}/CtrB({i})',                False),
  ('NI_CtrZ',               '{dev}/CtrZ({i})',                False),
  ('NI_CtrArmStartTrigger', '{dev}/CtrArmStartTrigger({i})',  False),
  ('NI_CtrInternalOutput',  '{dev}/CtrInternalOutput({i})',   False),
  ('NI_CtrOut',             '{dev}/CtrOut({i})',              False),
)

def entry(native, arbwave, ext_in=False, ext_out=False):
  return dict(
    native  = native,
    arbwave = arbwave,
    external_in = ext_in,
    external_out = ext_out,
  )

def ni_fmt(ni_name):
  m = re.match('(?P<dev>[^_]+)_(?P<sig>[^_]+)$', ni_name)
  if m:
    return '{}/{}'.format(m.group('dev').lower(), m.group('sig'))
  return ni_name

def ni_names(host, dev):
  def fN(fun,fmt,i, ext):
    return entry(
      '{}({})'.format(fun,i), fmt.format(host=host,dev=dev,i=i), ext, ext)

  # first load all of the functions into the value->name dictionary
  name_dict = dict()
  for fun,fmt,ext in ni_macros:
    f = getattr(comedi, fun)
    name_dict.update({
      f(i):fN(fun,fmt,i, ext) for i in xrange(1 + f(-1) - f(0))
    })

  # now load all the static names; start with those that do not begin with NI_
  name_dict[comedi.PXI_Star]  = entry('PXI_Star',  'PXI_Star')
  name_dict[comedi.PXI_Clk10] = entry('PXI_Clk10', 'PXI_Clk10')
  # finish static names by loading all in the ni_common_signal_names enum
  name_dict.update({
    v:entry(k, dev+'/'+ni_fmt(k[3:])) for k,v in comedi.__dict__.iteritems()
    if (k.startswith('NI_') and
        comedi.NI_COUNTER_NAMES_MAX < v < (comedi.NI_NAMES_BASE + comedi.NI_NUM_NAMES))
  })
  return name_dict


kernel_module_to_namefunc = {
  'ni_pcimio' : ni_names,
}

def get_signal_names(kernel_module, host_prefix, device_prefix):
  return kernel_module_to_namefunc \
    .get(kernel_module, lambda h,d:dict())(host_prefix, device_prefix)
