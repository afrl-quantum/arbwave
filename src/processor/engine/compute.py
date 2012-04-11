# vim: ts=2:sw=2:tw=80:nowrap

from numpy import MachAr
import bisect

from ... import backend
from .. import functions
from common import *
import physical

machine_arch = MachAr()
def cmpeps( a, b, scale_eps=1.0 ):
  if a < (b-machine_arch.eps*scale_eps):
    return -1
  elif a > (b+machine_arch.eps*scale_eps):
    return 1
  else:
    return 0


class UniqueElement:
  """
  This element representation only allows waveform elements that do _not_
  overlap.
  """
  def __init__(self, t, dt, value, group):
    self.t = t
    self.dt = dt
    self.value = value
    self.group = group
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
    return '({t},{dt},{v},g={g})' \
      .format(t=self.t,dt=self.dt,v=self.value,g=self.group)



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
  channel_info = dict()
  for c in channels:
    channel_info[c] = {'type':None, 'elements': list()}

  # go through each group and each element in each group
  ZT = 0*physical.unit.ms
  t = ZT
  groupNum = 0
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
    ZT.unitsMatch(t_start, 'expected dimensions of time')
    try:    dt,  ddt = eval( group['duration'], globals, L )
    except: dt = ddt = eval( group['duration'], globals, L )
    assert (dt > ZT and ddt > ZT), 'durations MUST be > 0!'
    assert ddt <= dt, 'ddt MUST be <= dt!'

    t_locals = dict()
    for e in group['elements']:
      chan = e['channel']
      ci = channel_info[chan]
      if not ( chan and e['enable'] and channels[chan]['enable'] ):
        continue

      dev = channels[chan]['device']
      if not dev:
        continue

      # determine clock precision
      clock_period = 1e-5*physical.unit.s # temporary fake clock

      if ci['type']:
        pass
      if   dev.startswith('Analog/')  or dev in backend.analog:
        ci['type'] = 'analog'
      elif dev.startswith('Digital/') or dev in backend.digital:
        ci['type'] = 'digital'
      else:
        raise RuntimeError("Cannot determine type of channel '"+chan+"'")

      L['dt'] = dt
      L['ddt'] = ddt

      # 2a. establish local start time / durations for element
      t_locals.setdefault(chan, t_start)
      L['t'] = t_locals[ chan ]
      t_start_e = eval( e['time'], globals, L )
      ZT.unitsMatch(t_start_e, 'expected dimensions of time')
      if not e['duration']:
                dt_e,  ddt_e = dt, ddt
      else:
        try:    dt_e,  ddt_e = eval( e['duration'], globals, L )
        except: dt_e = ddt_e = eval( e['duration'], globals, L )
      assert (dt_e > ZT and ddt_e > ZT), 'durations MUSt be > 0!'
      assert ddt_e <= dt_e, 'ddt MUST be <= dt!'

      # ensure that transitions occur on clock pulses...
      t_start_e = clock_period * round(t_start_e/clock_period)
      t_locals[chan] = max(t_locals[chan], t_start_e+dt_e)
      dt_e      = clock_period * (round(dt_e/clock_period) - 1)
      # for ddt_e, we first try to get the closest integer number of steps
      # then, we find the closest integer number of steps that coincide with
      # with clock pulses
      ddt_e     = dt_e / round(dt_e/ddt_e)
      ddt_e     = clock_period * int(ddt_e/clock_period)

      assert (dt_e > ZT and ddt_e > ZT), 'durations MUSt be > 0!'
      assert ddt_e <= dt_e, 'ddt MUST be <= dt!'

      L['dt'] = dt_e
      L['ddt'] = ddt_e

      ce = ci['elements']
      # support built-in functions such as ramp(to=,exponent=)
      # these use normalized time
      Vi = None
      if ce:
        Vi = ce[-1].value
      funs = functions.get(Vi, ddt_e/dt_e)
      L.update( funs )

      t_end_e = t_start_e + dt_e
      t_e = t_start_e
      while cmpeps(t_e, t_end_e, physical.unit.s) < 0:
        L['t'] = t_e

        # change time for built-in functions
        t_rel = (t_e - t_start_e) / dt_e
        for f in funs.values(): f.t = t_rel

        value = eval( e['value'], globals, L )
        placement = 0.0
        if type(value) in [list, tuple]:
          value, placement = value
          assert placement >= 0.0 and placement <= 1.0, \
            "timestep placement must be >=0 and <=1"

        # TODO:  apply scaling and range checks...

        if   ci['type'] is 'analog':
          physical.unit.V.unitsMatch( value, 'analog channels expect units=V' )
          #value = float(value) # set value in SI units
        elif ci['type'] is 'digital':
          assert type(value) in [bool, int, float], \
            'digital channels must have [True,False,==0,!=0] type of values'
          #value = bool(value) # set value as boolean
        else:
          raise RuntimeError("type of channel '"+chan+"' reset?!")

        t_e_si = float(t_e + placement*ddt_e)
        ddt_e_si = float( min(clock_period, (1.-placement)* ddt_e) )

        # insert (t, dt, value) tuple in SI units
        bisect.insort_right( ce, UE(t_e_si, ddt_e_si, value, groupNum) )
        transitions.append( t_e_si )

        t_e += ddt_e


    if not group['asynchronous']:
      t = max(t, t_start+dt)
    groupNum += 1

  # ensure that we have a unique set of transitions
  transitions = set(transitions)

  # the return values are initially empty
  analog = dict()
  digital = dict()

  for ci in channel_info.items():
    if   ci[1]['type'] is 'analog':
      analog[ ci[0] ] = to_plottable( ci[1]['elements'] )
    elif ci[1]['type'] is 'digital':
      digital[ ci[0] ] = to_plottable( ci[1]['elements'] )
    elif not ( ci[1]['type'] and ci[1]['elements'] ):
      pass
    else:
      raise RuntimeError("type of channel '"+ci[0]+"' reset?!")

  return analog, digital, transitions

def to_plottable( elem ):
  retval = dict()
  for e in elem:
    if e.group not in retval:
      retval[e.group] = list()
    retval[e.group].append( (e.t, 1, e.value) )

  return retval
