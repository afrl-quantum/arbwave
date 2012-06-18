
def load_nidaqmx_h(module):
  nidaqmx_version = module.get_nidaqmx_version()
  nidaqmx_h_name = 'nidaqmx_h_%s' % (nidaqmx_version.replace ('.', '_'))
  exec 'from nidaqmx import %s as nidaqmx_h' % (nidaqmx_h_name)
  d = nidaqmx_h.__dict__
  for name, value in d.items():
    if name.startswith ('_'): continue
    exec 'module.libnidaqmx.%s = %r' % (name, value)



class Task:
  def __init__(self, name, channels=[]):
    self.name = name
    self.channels = channels
    self.regen = False



class NiDAQmx:
  def __init__(self):
    self.last_task = -1
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
    return 0


  def DAQmxDisconnectTerms(self, src, dest):
    return 0


  def DAQmxTristateOutputTerm(self, term):
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
    self.tasks.pop(task.value)
    return 0


  def DAQmxIsTaskDone(self,task,bool_ref):
    bool_ref._obj.value = True
    return 0


  def DAQmxStartTask(self,task):
    print 'starting task: ', task
    return 0


  def DAQmxStopTask(self,task):
    print 'stopping task: ', task
    return 0


  def DAQmxGetTaskNumChans(self, retval_ref):
    retval_ref._obj.value = len(self.tasks[task.value].channels)
    return 0


  def DAQmxGetTaskChannels(self,task,buf_ref,bufsize):
    buf_ref._obj.value = ','.join(self.tasks[task.value].channels)[:bufsize]
    return 0


  def DAQmxGetTaskDevices(self,task,buf_ref,bufsize):
    devs = { c.partition('/')[0]:None  for c in self.tasks[task.value].channels }
    buf_ref._obj.value = ','.join(devs.keys())[:bufsize]
    return 0


  def DAQmxTaskControl(self,task,state_val):
    return 0


  def DAQmxCfgSampClkTiming(self, task, source, rate, active_edge_val,
                            sample_mode_val, samples_per_channel ):
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


  regen_modes = {
    True  : 10097, #DAQmx_Val_AllowRegen
    False : 10158, # DAQmx_Val_DoNotAllowRegen

    10097 : True,  #DAQmx_Val_AllowRegen
    10158 : False, # DAQmx_Val_DoNotAllowRegen
  }

  def DAQmxGetWriteRegenMode(self, task, retval_ref):
    retval_ref._obj.value = self.regen_modes[self.tasks[task.value].regen]
    return 0


  def DAQmxSetWriteRegenMode(self, task, val):
    self.tasks[task.value].regen = self.regen_modes[val]
    return 0
