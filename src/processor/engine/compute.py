# vim: ts=2:sw=2:tw=80:nowrap

from scipy.interpolate import UnivariateSpline
import numpy as np
import bisect

from ... import backend
from .. import functions
from common import *
import physical
from physical import unit

machine_arch = np.MachAr()
def cmpeps( a, b, scale_eps=1.0 ):
  if a < (b-machine_arch.eps*scale_eps):
    return -1
  elif a > (b+machine_arch.eps*scale_eps):
    return 1
  else:
    return 0

class OverlapError(Exception):
  pass

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
      raise OverlapError('overlapping waveform elements compared [' \
                         + str(self) + ',' + str(other) + ']!')

  def __repr__(self):
    return '({t},{dt},{v},g={g})' \
      .format(t=self.t,dt=self.dt,v=self.value,g=self.group)



def make_univariate_spline(scaling,order=1,smooth=0, globals=globals(), clamp_ends=True):
  # we have to first evaluate everything, build an array, and sort
  L = dict()
  for x,y in scaling:
    if x and y:
      yval = eval(y,globals)
      assert 'units' not in dir(yval), 'expected unitless scaler'
      L[eval(x,globals)] = yval
  # make sure that the order of data is correct
  L = L.items()
  L.sort(key=lambda v: v[0]) # sort by x
  L = np.array(L)


  # make sure the split the axes
  s = UnivariateSpline(L[:,1], L[:,0], k=order, s=smooth)

  if not clamp_ends:
    return s

  mn, mx   = L[0,1], L[-1,1]
  fmn, fmx = L[0,0], L[-1,0]
  del L

  def fun_clamp(x, *args,**kwargs):
    if x < mn:
      return fmn
    elif x > mx:
      return fmx
    return s(x, *args, **kwargs)

  return fun_clamp


def set_units_and_scaling(chname, ci, chan, globals):
  if not ci['unit_conversion_ratio']:
    if chan['units']:
      ci['units'] = eval(chan['units'], globals)
      if type(ci['units']) is physical.base.Quantity:
        ci['units'].coeff = 1.0

      ci['unit_conversion_ratio'] = unit.V / ci['units']

    elif ci['type'] is 'analog':
      ci['unit_conversion_ratio'] = unit.V
  if (not ci['scaling']) and chan['scaling']:
    assert ci['units'], \
      chname+': dimensions required for scaling'
    assert chan['interp_order'], \
      chname+': expected interpolation order for scaling'
    assert chan['interp_smoothing']>=0, \
      chname+': expected interpolation smoothing >=0 for scaling'
    ci['scaling'] = make_univariate_spline(
      chan['scaling'],
      chan['interp_order'],
      chan['interp_smoothing'],
      globals=globals,
    )




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
  channel_info = make_channel_info(channels)

  # go through each group and each element in each group
  ZT = 0*unit.ms
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

    max_time = 0.0

    t_locals = dict()
    for e in group['elements']:
      chname = e['channel']
      ci = channel_info[chname]
      chan = channels[chname]
      if not ( chname and e['enable'] and chan['enable'] ):
        continue

      dev = chan['device']
      if not dev:
        continue

      # determine clock precision
      clock_period = 1e-5*unit.s # temporary fake clock

      if not ci['type']:
        ci['type'] = determine_channel_type(chname, dev)


      set_units_and_scaling(chname, ci, chan, globals)

      L['dt'] = dt
      L['ddt'] = ddt

      # 2a. establish local start time / durations for element
      t_locals.setdefault(chname, t_start)
      L['t'] = t_locals[ chname ]
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
      t_locals[chname]  = max(t_locals[chname], t_start_e+dt_e)

      # get the closest integer number of steps
      ddt_e     = dt_e / round(dt_e/ddt_e)

      assert (dt_e > ZT and ddt_e > ZT), 'durations MUSt be > 0!'
      assert ddt_e <= dt_e, 'ddt MUST be <= dt!'

      L['dt'] = dt_e
      L['ddt'] = ddt_e

      ce = ci['elements']
      # support built-in functions such as ramp(to=,exponent=)
      # these use normalized time
      Vi = ci['last']

      funs = functions.get(Vi, ddt_e/dt_e)
      L.update( funs )

      t_end_e = clock_period * (round((t_start_e + dt_e)/clock_period) - 1)
      t_e = t_start_e
      while cmpeps(t_e, t_end_e, unit.s) < 0:
        # fix times to be exactly on a clock pulse...
        t_e_fixed = clock_period * round(t_e/clock_period)

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

        # store last value _before_ scaling
        ci['last'] = value


        value = apply_scaling(value, chname, ci) 

        check_final_units( value, chname, ci )

        # fix again after applying  placement...
        if placement > 0.0:
          t_e_fixed = clock_period * round((t_e + placement*ddt_e)/clock_period -1)
        ddt_e_fixed = t_e + ddt_e - t_e_fixed


        t_e_si = float(t_e_fixed)
        ddt_e_si = float( max(clock_period, ddt_e_fixed) )

        # insert (t, dt, value) tuple in SI units
        max_time = max( max_time, t_e_si + ddt_e_si )
        try:
          bisect.insort_right( ce, UE(t_e_si, ddt_e_si, value, groupNum) )
        except OverlapError, e:
          raise OverlapError( '{c}: {e}'.format(c=chname,e=e) )
        transitions.append( t_e_si )

        t_e += ddt_e

    transitions.append( max_time )

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



def apply_scaling(value, chname, ci):
  # apply scaling and range checks...
  if not ci['scaling']:
    if ci['unit_conversion_ratio']:
      value *= ci['unit_conversion_ratio']
    # else required to be in volts or is a boolean
  else:
    assert ci['units'], chname+':  dimensions required for scaling'
    value /= ci['units']
    assert type(value) is not physical.base.Quantity, \
      chname+':  wrong units: {}, expected [{}]'.format(e['value'], ci['units'])
    value = ci['scaling'](value)*unit.V

  return value



def make_channel_info(channels):
  D = dict()
  for c in channels:
    D[c] = {
      'type':None,
      'elements': list(),
      'scaling' : None,
      'unit_conversion_ratio' : None,
      'last' : None,
    }
  return D



def determine_channel_type(chname, dev):
  if   dev.startswith('Analog/')  or dev in backend.analog:
    return 'analog'
  elif dev.startswith('Digital/') or dev in backend.digital:
    return 'digital'
  raise RuntimeError(chname+':  Cannot determine type of channel ')



def check_final_units( value, chname, ci ):
  if   ci['type'] is 'analog':
    unit.V.unitsMatch( value, 'analog channels expect units=V' )
    #value = float(value) # set value in SI units
  elif ci['type'] is 'digital':
    if type(value) not in [bool, int, float]:
      raise TypeError(
        'Found digital channel with type: {}\n' \
        'digital channels value types must be [True,False,==0,!=0]\n' \
        .format(type(value))
      )
    #value = bool(value) # set value as boolean
  else:
    raise RuntimeError("type of channel '"+chname+"' reset?!")
