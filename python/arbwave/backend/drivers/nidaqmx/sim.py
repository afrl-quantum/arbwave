# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level nidaqmx library.
"""

import re, ctypes
from itertools import chain
import nidaqmx
from logging import log, debug, info, warn, error, critical, DEBUG

regen_modes = None
ch_types = None
polarity_map = None

def load_nidaqmx_h(module):
  nidaqmx_version = module.get_nidaqmx_version()
  nidaqmx_h_name = 'nidaqmx_h_%s' % (nidaqmx_version.replace ('.', '_'))
  exec 'from nidaqmx import %s as nidaqmx_h' % (nidaqmx_h_name)
  module.libnidaqmx.DAQmx     = nidaqmx_h.DAQmx
  module.libnidaqmx.error_map = nidaqmx_h.error_map

  global regen_modes, ch_types, polarity_map
  l = module.libnidaqmx
  regen_modes = {
    True  : l.DAQmx.Val_AllowRegen,
    False : l.DAQmx.Val_DoNotAllowRegen,

    l.DAQmx.Val_AllowRegen      : True,
    l.DAQmx.Val_DoNotAllowRegen : False,
  }
  ch_types = {
    'ai':l.DAQmx.Val_AI, 'ao':l.DAQmx.Val_AO,
    'di':l.DAQmx.Val_DI, 'do':l.DAQmx.Val_DO,
    'ci':l.DAQmx.Val_CI, 'co':l.DAQmx.Val_CO,
  }
  polarity_map = {
    l.DAQmx.Val_InvertPolarity      : True,
    l.DAQmx.Val_DoNotInvertPolarity : False,
  }


class Channel:
  def __init__(self, name, typ):
    self.name = name
    self.typ = typ

  def __str__(self):
    return self.name

  def __repr__(self):
    return str(self)


class Task:
  def __init__(self, name):
    self.name = name
    self.channels = list()
    self.regen = False
    self.chindx = dict()

  def add_channel(self, ch):
    # we first make sure that only channel types of the same exist
    for c in self.channels:
      assert c.typ == ch.typ, \
        'NIDAQmx:  only similar channel types allowed in same task'
    self.chindx[str(ch)] = len( self.channels )
    self.channels.append( ch )



class NiDAQmx:
  def __init__(self):
    self.last_task = 0
    self.tasks = dict()


  #   SYSTEM INFORMATION
  def DAQmxGetSysNIDAQMajorVersion(self, retval_ref):
    retval_ref._obj.value = 8
    log(DEBUG-1, 'DAQmxGetSysNIDAQMajorVersion() = %s', retval_ref._obj.value)
    return 0


  def DAQmxGetSysNIDAQMinorVersion(self, retval_ref):
    retval_ref._obj.value = 0
    log(DEBUG-1, 'DAQmxGetSysNIDAQMinorVersion() = %s', retval_ref._obj.value)
    return 0


  def DAQmxGetSysDevNames(self,buf_ref,bufsize):
    buf_ref._obj.value = 'Dev1, Dev2, Dev3'[:bufsize]
    log(DEBUG-1, 'DAQmxGetSysDevNames() = %s', buf_ref._obj.value)
    return 0


  def DAQmxGetSysTasks(self,buf_ref,bufsize):
    buf_ref._obj.value = ''[:bufsize]
    log(DEBUG-1, 'DAQmxGetSysTasks(%s) = %s', chan, buf_ref._obj.value)
    return 0


  def DAQmxGetSysGlobalChans(self,buf_ref,bufsize):
    buf_ref._obj.value = ''[:bufsize]
    log(DEBUG-1, 'DAQmxGetSysGlobalChans(%s) = %s', chan, buf_ref._obj.value)
    return 0



  # PHYSICAL CHANNEL INFORMATION
  def DAQmxGetPhysicalChanDOSampClkSupported(self, chan, retval_ref):
    log(DEBUG-1, 'DAQmxGetPhysicalChanDOSampClkSupported(%s) = %s', chan, retval_ref._obj.value)
    retval_ref._obj.value = 0x1 # false for PCI-6723, but let's set true anyway
    return 0



  # SIGNALS & ROUTES
  def DAQmxConnectTerms(self, src, dest, invert):
    log(DEBUG-1, 'DAQmxConnectTerms(%s,%s,%s)', src, dest, polarity_map[invert])
    return 0


  def DAQmxDisconnectTerms(self, src, dest):
    log(DEBUG-1, 'DAQmxDisonnectTerms(%s,%s)', src, dest)
    return 0


  def DAQmxTristateOutputTerm(self, term):
    log(DEBUG-1, 'DAQmxTristateOutputTerm(%s)', term)
    return 0




  #   DEVICE INFORMATION
  def DAQmxGetDevProductType(self, dev, buf_ref, bufsize):
    # for now, we will default to simulating a PCI-6723 ao card
    buf_ref._obj.value = 'PCI-6229'[:bufsize]
    log(DEBUG-1, 'DAQmxGetDevProductType(%s) = %s', dev, buf_ref._obj.value)
    return 0


  def DAQmxGetDevProductNum(self, dev, retval_ref):
    retval_ref._obj.value = 0x2A
    log(DEBUG-1, 'DAQmxGetDevProductNum(%s) = %s', dev, retval_ref._obj.value)
    return 0


  def DAQmxGetDevSerialNum(self, dev, retval_ref):
    retval_ref._obj.value = 0xDEADBEEF
    log(DEBUG-1, 'DAQmxGetDevSerialNum(%s) = %s', dev, retval_ref._obj.value)
    return 0


  def DAQmxGetDevAOPhysicalChans(self, dev, buf_ref, bufsize):
    chans = ','.join([ '{}/ao{}'.format(dev,i) for i in xrange(32) ])
    buf_ref._obj.value = chans[:bufsize]
    log(DEBUG-1, 'DAQmxGetDevAOPhysicalChans(%s) = %s', dev, buf_ref._obj.value)
    return 0


  def DAQmxGetDevDOLines(self, dev, buf_ref, bufsize):
    # this is not really consistent right now, but we're simulating 32 lines
    chans = ','.join( chain(* [
      [ '{}/port{}/line{}'.format(dev,pi,li) for li in xrange(8) ]
      for pi in xrange(4)
    ]) )
    buf_ref._obj.value = chans[:bufsize]
    log(DEBUG-1, 'DAQmxGetDevDOLines(%s) = %s', dev, buf_ref._obj.value)
    return 0


  def DAQmxGetDevCOPhysicalChans(self, dev, buf_ref, bufsize):
    buf_ref._obj.value = '{0}/ctr0,{0}/ctr1'.format(dev)[:bufsize]
    log(DEBUG-1, 'DAQmxGetDevCOPhysicalChans(%s) = %s', dev, buf_ref._obj.value)
    return 0


  def DAQmxGetDevAOSampClkSupported(self, dev, retval_ref):
    retval_ref._obj.value = 0x1
    log(DEBUG-1, 'DAQmxGetDevAOSampClkSupported(%s) = %s', dev, retval_ref._obj.value)
    return 0

  def DAQmxResetDevice(self, dev):
    log(DEBUG-1, 'DAQmxResetDevice(%s)', dev)
    return 0



  #   TASK INFORMATION
  def DAQmxCreateTask(self,name,task_ref):
    self.last_task += 1
    task_ref._obj.value = self.last_task
    self.tasks[ self.last_task ] = Task(name)
    log(DEBUG-1, 'DAQmxCreateTask(%s) = %d', name, self.last_task)
    return 0


  def DAQmxGetTaskName(self,task,buf_ref,bufsize):
    buf_ref._obj.value = self.tasks[task.value].name[:bufsize]
    log(DEBUG-1, 'DAQmxGetTaskName(%s) = %s', task, buf_ref._obj.value)
    return 0


  def DAQmxClearTask(self,task):
    log(DEBUG-1, 'DAQmxClearTask(%s)', task)
    if task.value in self.tasks:
      self.tasks.pop(task.value)
    return 0


  def DAQmxIsTaskDone(self,task,bool_ref):
    log(DEBUG-1, 'DAQmxIsTaskDone(%s) = True', task)
    bool_ref._obj.value = True
    return 0


  def DAQmxStartTask(self,task):
    log(DEBUG-1, 'DAQmxStartTask(%s)', task)
    return 0


  def DAQmxStopTask(self,task):
    log(DEBUG-1, 'DAQmxStopTask(%s)', task)
    return 0


  def DAQmxCreateAOVoltageChan(self,task, phys_chan, chname,
                               min_val, max_val, units, custom_scale_name):
    log(DEBUG-1, 'DAQmxCreateAOVoltageChan(%s,%s,%s,%g,%g,%d,%s)', task, phys_chan, chname, min_val, max_val, units, custom_scale_name)
    assert phys_chan, 'NIDAQmx:  missing physical channel name'
    if not chname:
      chname = phys_chan
    T = self.tasks[ task.value ]
    assert chname not in T.channels, \
      'NIDAQmx:  channel already exists in task'
    T.add_channel( Channel(chname, 'ao') )
    return 0


  def DAQmxCreateDOChan(self,task, phys_chan, chname, grouping_val):
    log(DEBUG-1, 'DAQmxCreateDOChan(%s,%s,%s,%d)', task, phys_chan, chname, grouping_val)
    assert phys_chan, 'NIDAQmx:  missing physical DO channel name(s)'
    assert grouping_val==nidaqmx.libnidaqmx.DAQmx.Val_ChanPerLine, \
      'only per_line DO group ing implemented in simulator'
    if not chname:
      chname = phys_chan
    T = self.tasks[ task.value ]
    assert chname not in T.channels, \
      'NIDAQmx:  channel already exists in task'
    T.add_channel( Channel(chname, 'do') )
    return 0


  def DAQmxGetChanType(self, task, chname, retval_ref):
    T = self.tasks[ task.value ]
    if chname:
      retval_ref._obj.value = ch_types[ T.channels[ T.chindx[chname] ].typ ]
    else:
      retval_ref._obj.value = ch_types[ T.channels[ 0 ].typ ]
    log(DEBUG-1, 'DAQmxGetChanType(%s,%s) = %s', task, chname, retval_ref._obj.value)
    return 0


  def DAQmxGetTaskNumChans(self, task, retval_ref):
    retval_ref._obj.value = len(self.tasks[task.value].channels)
    log(DEBUG-1, 'DAQmxGetTaskNumChans(%s) = %s', task, retval_ref._obj.value)
    return 0


  def DAQmxGetTaskChannels(self,task,buf_ref,bufsize):
    chnames = [ str(c)  for c in self.tasks[task.value].channels ]
    buf_ref._obj.value = ','.join(chnames)[:bufsize]
    log(DEBUG-1, 'DAQmxGetTaskChannels(%s) = %s', task, buf_ref._obj.value)
    return 0


  def DAQmxGetTaskDevices(self,task,buf_ref,bufsize):
    devs = { c.name.partition('/')[0] for c in self.tasks[task.value].channels }
    buf_ref._obj.value = ','.join(devs)[:bufsize]
    log(DEBUG-1, 'DAQmxGetTaskDevices(%s) = %s', task, buf_ref._obj.value)
    return 0


  def DAQmxTaskControl(self,task,state_val):
    log(DEBUG-1, 'DAQmxTaskControl(%s,%s)', task, state_val.value)
    return 0


  def DAQmxSetSampTimingType(self, task, timing_type):
    log(DEBUG-1, 'DAQmxSetSampTimingType(%s,%d)', task, timing_type.value)
    return 0


  def DAQmxSetSampQuantSampMode(self, task, mode):
    log(DEBUG-1, 'DAQmxSetSampQuantMode(%s,%d)', task, mode.value)
    return 0


  def DAQmxSetSampQuantSampPerChan(self, task, n):
    log(DEBUG-1, 'DAQmxSetSampQuantSampPerChan(%s,%d)', task, n.value)
    return 0


  def DAQmxCfgSampClkTiming(self, task, source, rate, active_edge_val,
                            sample_mode_val, samples_per_channel ):
    log(DEBUG-1, 'DAQmxCfgSampClkTiming(%s, %s, %f, %s, %s, %d)',
      task, source, rate.value,
      task.edge_rmap[active_edge_val],
      task.sample_mode_rmap[sample_mode_val],
      samples_per_channel.value)
    return 0


  def DAQmxGetSampClkMaxRate(self, task, retval_ref):
    log(DEBUG-1, 'DAQmxGetSampClkMaxRate(%s) = %d', task, 2e6)
    # we'll return the value for the PCI-6723
    #retval_ref._obj.value = 800e3
    # what the heck. let's return a larger value!
    retval_ref._obj.value = 2e6
    return 0


  def DAQmxCfgDigEdgeStartTrig(self, task, source, edge_val):
    log(DEBUG-1, 'DAQmxCfgDigEdgeStartTrig(%s,%s,%d)', task, source, edge_val)
    return 0


  def DAQmxDisableStartTrig(self, task):
    log(DEBUG-1, 'DAQmxDisableStartTrig(%s)', task)
    return 0


  def DAQmxGetBufAOOnbrdBufSize(self, task, retval_ref):
    log(DEBUG-1, 'DAQmxGetBufAOOnbrdBufSize(%s) = %d', task, 2**14)
    retval_ref._obj.value = 2**14
    return 0

  def DAQmxGetBufDOOnbrdBufSize(self, task, retval_ref):
    log(DEBUG-1, 'DAQmxGetBufDOOnbrdBufSize(%s) = %d', task, 2**14)
    retval_ref._obj.value = 2**14
    return 0


  def DAQmxGetBufAOBufSize(self, task, retval_ref):
    log(DEBUG-1, 'DAQmxGetBufAOBufSize(%s) = %d', task, 2**16)
    retval_ref._obj.value = 2**16
    return 0

  def DAQmxGetBufDOBufSize(self, task, retval_ref):
    log(DEBUG-1, 'DAQmxGetBufDOBufSize(%s) = %d', task, 2**16)
    retval_ref._obj.value = 2**16
    return 0


  def DAQmxWaitUntilTaskDone(self, task, timeout):
    log(DEBUG-1, 'DAQmxWaitUntilTaskDone(%s,%f)', task, timeout.value)
    return 0


  def DAQmxGetWriteRegenMode(self, task, retval_ref):
    retval_ref._obj.value = regen_modes[self.tasks[task.value].regen]
    log(DEBUG-1, 'DAQmxGetWriteRegenMode(%s) = %s',
      task, self.tasks[task.value].regen)
    return 0


  def DAQmxSetWriteRegenMode(self, task, val):
    log(DEBUG-1, 'DAQmxSetWriteRegenMode(%s,%s)', task, regen_modes[val])
    self.tasks[task.value].regen = regen_modes[val]
    return 0


  def DAQmxWriteAnalogF64(self, task, n_per_chan, auto_start, timeout, layout,
                          data, n_written_ref, ignored):
    cdata = ctypes.cast( data, ctypes.POINTER(ctypes.c_double))
    log(DEBUG-1, 'DAQmxWriteAnalogF64(%s,%d,%s,%f,%d,%s,n_written_ref, None)',
      task, n_per_chan.value, bool(auto_start.value), timeout.value, layout,
      cdata[0:(n_per_chan.value * len(self.tasks[task.value].channels))] )
    n_written_ref._obj.value = n_per_chan.value
    return 0


  def DAQmxWriteDigitalLines(self, task, n_per_chan, auto_start, timeout, layout,
                          data, n_written_ref, ignored):
    cdata = ctypes.cast( data, ctypes.POINTER(ctypes.c_uint8))
    log(DEBUG-1, 'DAQmxWriteAnalogF64(%s,%d,%s,%f,%d,%s,n_written_ref, None)',
      task, n_per_chan, bool(auto_start.value), timeout.value, layout,
      cdata[0:(n_per_chan * len(self.tasks[task.value].channels))] )
    n_written_ref._obj.value = n_per_chan
    return 0
