# vim: ts=2:sw=2:tw=80:nowrap

import bisect
from common import *
import physical
from numpy import MachAr

machine_arch = MachAr()
def cmpeps( a, b ):
  if a < (b-machine_arch.eps):
    return -1
  elif a > (b+machine_arch.eps):
    return 1
  else:
    return 0


class UniqueElement:
  """
  This element representation only allows waveform elements that do _not_
  overlap.
  """
  def __init__(self, t, dt, value):
    self.t = t
    self.dt = dt
    self.value = value
  def __cmp__(self, other):
    if self.t < other.t and cmpeps((self.t+self.dt), other.t) <=0:
      return -1
    elif other.t < self.t and cmpeps((other.t+other.dt), self.t) <=0:
      return 1
    #elif cmpeps(self.t, other.t)==0 and cmpeps(self.dt, other.dt)==0:
    #  return 0
    else:
      raise KeyError('overlapping waveform elements compared [' \
                     + str(self) + ',' + str(other) + ']!')

  def __repr__(self):
    return '('+str(self.t)+','+str(self.dt)+','+str(self.value)+')'



def waveforms( channels, waveforms, signals, globals=None ):
  """
  Take the configuration as provided by the user and generate a set of waveforms
  that can then be sent to the plotter and/or a hardware driver for output.

  This process is done in two major steps:
    1.  Determine all times that must make a voltage transition on some channel.
    2.  Generate a voltage sample for each transition that must occur.
  """
  exec global_load
  UE = UniqueElement

  transitions = list()
  channel_elements = dict()
  for c in channels: channel_elements[c] = list()

  ZT = 0*physical.unit.ms
  t = ZT
  for group in waveforms:
    if not ( group['enable'] and group['elements'] ):
      continue

    # 1.  evaluate local script environment
    # 2.  establish local start time/durations of group
    # 3.  loop through each element in the group
    #   a.  establish local start time of element (depends on local group start
    #       time as well as consecutive elements of the same channel)
    #   b.  save explicit transition time to 'transitions' array
    #   c.  save explicit (t,dt,value) tuple to channel dictionary
    #       This is expected to be non-overlapping using the bisect.insort_right
    #       function with the UniqueElement class.

    # 1.  evaluate local script environment
    L = dict()
    if group['script']:
      exec group['script'] in globals, L

    # 2.  establish local start time and durations...
    L['t'] = t
    t_start = eval( group['time'], globals, L )
    try:    dt,  ddt = eval( group['duration'], globals, L )
    except: dt = ddt = eval( group['duration'], globals, L )
    assert (dt > ZT and ddt > ZT), 'durations MUST be > 0!'
    assert ddt <= dt, 'ddt MUST be <= dt!'

    t_locals = dict()
    for e in group['elements']:
      chan = e['channel']

      if not ( chan and e['enable'] and channels[chan]['enable'] ):
        continue

      L['dt'] = dt
      L['ddt'] = ddt

      # 2a. establish local start time / durations for element
      t_locals.setdefault(chan, t_start)
      L['t'] = t_locals[ chan ]
      t_start_e = eval( e['time'], globals, L )
      if not e['duration']:
                dt_e,  ddt_e = dt, ddt
      else:
        try:    dt_e,  ddt_e = eval( e['duration'], globals, L )
        except: dt_e = ddt_e = eval( e['duration'], globals, L )
      assert (dt_e > ZT and ddt > ZT), 'durations MUSt be > 0!'
      assert ddt_e <= dt_e, 'ddt MUST be <= dt!'

      L['dt'] = dt_e
      L['ddt'] = ddt_e

      ce = channel_elements[chan]
      t_end_e = t_start_e + dt_e
      t_e = t_start_e
      while t_e < t_end_e:
        transitions.append( float(t_e) ) # force SI units
        L['t'] = t_e

        # TODO:  support built-in functions such as ramp(to=,exponent=)
        value = eval( e['value'], globals, L )
        # TODO:  apply scaling and range checks...

        # insert (t, dt, value) tuple in SI units
        bisect.insort_right( ce, UE(float(t_e), float(ddt_e), float(value)) )

        t_e += ddt_e

      t_locals[chan] = max(t_locals[chan], t_end_e)


    if not group['asynchronous']:
      t = max(t, t_start+dt)

  # ensure that we have a unique set of transitions
  transitions = set(transitions)

  print 'transitions:', transitions
  print 'channel waveforms:', channel_elements


  analog = None
  digital = None

  return analog, digital
