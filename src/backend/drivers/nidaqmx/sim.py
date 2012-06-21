# vim: ts=2:sw=2:tw=80:nowrap
"""
Simulated low-level nidaqmx library.
"""

import re, ctypes
import nidaqmx
from logging import log, debug, info, warn, error, critical, DEBUG

regen_modes = None
ch_types = None
polarity_map = None

def load_nidaqmx_h(module):
  nidaqmx_version = module.get_nidaqmx_version()
  nidaqmx_h_name = 'nidaqmx_h_%s' % (nidaqmx_version.replace ('.', '_'))
  exec 'from nidaqmx import %s as nidaqmx_h' % (nidaqmx_h_name)
  d = nidaqmx_h.__dict__
  for name, value in d.items():
    if name.startswith ('_'): continue
    exec 'module.libnidaqmx.%s = %r' % (name, value)


  global regen_modes, ch_types, polarity_map
  l = module.libnidaqmx
  regen_modes = {
    True  : l.DAQmx_Val_AllowRegen,
    False : l.DAQmx_Val_DoNotAllowRegen,

    l.DAQmx_Val_AllowRegen      : True,
    l.DAQmx_Val_DoNotAllowRegen : False,
  }
  ch_types = {
    'ai':l.DAQmx_Val_AI, 'ao':l.DAQmx_Val_AO,
    'di':l.DAQmx_Val_DI, 'do':l.DAQmx_Val_DO,
    'ci':l.DAQmx_Val_CI, 'co':l.DAQmx_Val_CO,
  }
  polarity_map = {
    l.DAQmx_Val_InvertPolarity      : True,
    l.DAQmx_Val_DoNotInvertPolarity : False,
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
    return 0


  def DAQmxGetSysNIDAQMinorVersion(self, retval_ref):
    retval_ref._obj.value = 0
    return 0


  def DAQmxGetSysDevNames(self,buf_ref,bufsize):
    buf_ref._obj.value = 'Dev1'[:bufsize]
    return 0


  def DAQmxGetSysTasks(self,buf_ref,bufsize):
    buf_ref._obj.value = ''[:bufsize]
    return 0


  def DAQmxGetSysGlobalChans(self,buf_ref,bufsize):
    buf_ref._obj.value = ''[:bufsize]
    return 0



  # PHYSICAL CHANNEL INFORMATION
  def DAQmxGetPhysicalChanDOSampClkSupported(self, chan, retval_ref):
    retval_ref._obj.value = 0x1
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
    buf_ref._obj.value = 'PCI-6723'[:bufsize]
    return 0


  def DAQmxGetDevProductNum(self, dev, retval_ref):
    retval_ref._obj.value = 0x2A
    return 0


  def DAQmxGetDevSerialNum(self, dev, retval_ref):
    retval_ref._obj.value = 0xDEADBEEF
    return 0


  def DAQmxGetDevAOPhysicalChans(self, dev, buf_ref, bufsize):
    buf_ref._obj.value = 'Dev1/ao0,Dev1/ao1,Dev1/ao2,Dev1/ao3'[:bufsize]
    return 0


  def DAQmxGetDevDOLines(self, dev, buf_ref, bufsize):
    buf_ref._obj.value = 'Dev1/port0/line0,Dev1/port0/line1,Dev1/port0/line2'[:bufsize]
    return 0


  def DAQmxGetDevCOPhysicalChans(self, dev, buf_ref, bufsize):
    buf_ref._obj.value = 'Dev1/ctr0,Dev1/ctr1'[:bufsize]
    return 0


  def DAQmxGetDevAOSampClkSupported(self, dev, retval_ref):
    retval_ref._obj.value = 0x1
    return 0

  def DAQmxResetDevice(self, dev):
    return 0



  #   TASK INFORMATION
  def DAQmxCreateTask(self,name,task_ref):
    self.last_task += 1
    task_ref._obj.value = self.last_task
    self.tasks[ self.last_task ] = Task(name)
    return 0


  def DAQmxGetTaskName(self,task,buf_ref,bufsize):
    buf_ref._obj.value = self.tasks[task.value].name[:bufsize]
    return 0


  def DAQmxClearTask(self,task):
    if task.value in self.tasks:
      self.tasks.pop(task.value)
    return 0


  def DAQmxIsTaskDone(self,task,bool_ref):
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
    assert phys_chan, 'NIDAQmx:  missing physical channel name'
    if not chname:
      chname = phys_chan
    T = self.tasks[ task.value ]
    assert chname not in T.channels, \
      'NIDAQmx:  channel already exists in task'
    T.add_channel( Channel(chname, 'ao') )
    return 0


  def DAQmxGetChanType(self, task, chname, retval_ref):
    T = self.tasks[ task.value ]
    if chname:
      retval_ref._obj.value = ch_types[ T.channels[ T.chindx[chname] ].typ ]
    else:
      retval_ref._obj.value = ch_types[ T.channels[ 0 ].typ ]
    return 0


  def DAQmxGetTaskNumChans(self, task, retval_ref):
    retval_ref._obj.value = len(self.tasks[task.value].channels)
    return 0


  def DAQmxGetTaskChannels(self,task,buf_ref,bufsize):
    chnames = [ str(c)  for c in self.tasks[task.value].channels ]
    buf_ref._obj.value = ','.join(chnames)[:bufsize]
    return 0


  def DAQmxGetTaskDevices(self,task,buf_ref,bufsize):
    devs = { c.name.partition('/')[0] for c in self.tasks[task.value].channels }
    buf_ref._obj.value = ','.join(devs)[:bufsize]
    return 0


  def DAQmxTaskControl(self,task,state_val):
    return 0


  def DAQmxSetSampTimingType(self, task, timing_type):
    return 0


  def DAQmxSetSampQuantSampMode(self, task, mode):
    return 0


  def DAQmxSetSampQuantSampPerChan(self, task, n):
    return 0


  def DAQmxCfgSampClkTiming(self, task, source, rate, active_edge_val,
                            sample_mode_val, samples_per_channel ):
    log(DEBUG-1, 'DAQmxCfgSampClkTiming(%s, %s, %f, %s, %s, %d)',
      task, source, rate.value,
      task.edge_rmap[active_edge_val],
      task.sample_mode_rmap[sample_mode_val],
      samples_per_channel.value)
    return 0


  def DAQmxCfgDigEdgeStartTrig(self, task, source, edge_val):
    return 0


  def DAQmxDisableStartTrig(self, task):
    return 0


  def DAQmxGetBufAOOnbrdBufSize(self, task, retval_ref):
    retval_ref._obj.value = 2**14
    return 0

  DAQmxGetBufDOOnbrdBufSize = DAQmxGetBufAOOnbrdBufSize


  def DAQmxGetBufAOBufSize(self, task, retval_ref):
    retval_ref._obj.value = 2**16
    return 0

  DAQmxGetBufDOBufSize = DAQmxGetBufAOBufSize


  def DAQmxWaitUntilTaskDone(self, task, timeout):
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
