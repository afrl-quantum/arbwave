# vim: ts=2:sw=2:tw=80:nowrap
"""
  Driver specific singals inteligible to comedi.
"""

import logging, re
from logging import debug
import ctypes_comedi as c


class NullSignalLoader(object):
  def __init__(self, device):
    debug("signals for device '%s' not yet known", device)



class NISignalLoader(object):
  def __init__(self, device):
    
    #put None for unknown signals
    self.sig_nums_PFI = \
    {
     'Ctr0Gate':c.NI_PFI_OUTPUT_G_GATE0,
     'Ctr0InternalOutput':c.NI_PFI_OUTPUT_GOUT0,
     'Ctr0Source':c.NI_PFI_OUTPUT_G_SRC0,
     'Ctr1Gate':c.NI_PFI_OUTPUT_G_GATE1,
     'Ctr1InternalOutput':c.NI_PFI_OUTPUT_GOUT1,
     'Ctr1Source':c.NI_PFI_OUTPUT_G_SRC1,
     'FrequencyOutput':c.NI_PFI_OUTPUT_FREQ_OUT,
     'ChangeDetectionEvent':c.NI_PFI_OUTPUT_DIO_CHANGE_DETECT_RTSI, #best guess
     'ai/ConvertClock':c.NI_PFI_OUTPUT_AI_CONVERT,
     'ai/ReferenceTrigger':c.NI_PFI_OUTPUT_AI_START2,
     'ai/SampleClock':c.NI_PFI_OUTPUT_AI_START_PULSE ,
     'ai/StartTrigger':c.NI_PFI_OUTPUT_AI_START1,
     'ao/SampleClock':c.NI_PFI_OUTPUT_AO_UPDATE_N,
     'ao/StartTrigger':c.NI_PFI_OUTPUT_AO_START1,
     'di/StartTrigger':None,
     'do/StartTrigger':None
    }
    
    self.sig_nums_PFI.update({'RTSI'+str(i):c.NI_PFI_OUTPUT_RTSI(i) for i in xrange(8)})
    
    self.sig_nums_RTSI = \
    {
      '10MHsRefClock':c.NI_RTSI_OUTPUT_RTSI_OSC,
      'Ctr0Source':c.NI_RTSI_OUTPUT_G_SRC0,
      'Ctr0Gate':c.NI_RTSI_OUTPUT_G_GATE0,
      'Ctr0InternalOutput':c.NI_RTSI_OUTPUT_RGOUT0,
      'ao/StartTrigger':c.NI_RTSI_OUTPUT_DA_START1,
      'ao/SampleClock':c.NI_RTSI_OUTPUT_DACUPDN,
      'ai/StartTrigger':c.NI_RTSI_OUTPUT_ADR_START1,
      'ai/ReferenceTrigger':c.NI_RTSI_OUTPUT_ADR_START2
    }
    
    self.sig_nums_EXT = dict()
    self.sig_nums_EXT.update({'PFI'+str(i):c.NI_EXT_PFI(i) for i in xrange(16)})
    self.sig_nums_EXT.update({'RTSI'+str(i):c.NI_EXT_RTSI(i) for i in xrange(16)})
    
    self.sig_nums_AO_CLOCK = dict()
    self.sig_nums_AO_CLOCK.update({'PFI'+str(i):c.NI_AO_SCAN_BEGIN_SRC_PFI(i) for i in xrange(16)})
    self.sig_nums_AO_CLOCK.update({'RTSI'+str(i):c.NI_AO_SCAN_BEGIN_SRC_RTSI(i) for i in xrange(8)})
    #cheat for a test:
    self.sig_nums_AO_CLOCK.update({'Ctr1InternalOutput':c.NI_AO_SCAN_BEGIN_SRC_PFI(0)}) 
    
    self.ch_nums = dict()
    
    self.ch_nums.update({'PFI'+str(i):{'kind':'PFI','subdev':7,'chan':i} for i in xrange(16)})
    self.ch_nums.update({'RTSI'+str(i):{'kind':'RTSI','subdev':10,'chan':i} for i in xrange(8)})
    self.ch_nums.update({'ao/SampleClock':{'kind':'ao_clock'}})
    self.ch_nums.update({'ao/StartTrigger':{'kind':'trigger'}})
     
     
kernel_module_to_loader = {
  'ni_pcimio' : NISignalLoader,
}

def getSignalLoader( kernel_module ):
  return kernel_module_to_loader.get(kernel_module, NullSignalLoader)
