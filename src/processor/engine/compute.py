# vim: ts=2:sw=2:tw=80:nowrap

from scipy.interpolate import UnivariateSpline, interp1d
import numpy as np
import bisect, sys
from logging import log, info, debug, warn, critical, DEBUG, root as rootlog

from ... import backend
from .. import functions
import physical
from physical import unit
from math import ceil
from ...tools.scaling import calculate as calculate_scaling
from ...tools.eval import evalIfNeeded

machine_arch = np.MachAr()


class OverlapError(Exception):
  pass

class UniqueElement:
  """
  This element representation only allows waveform elements that do _not_
  overlap.
  """
  def __init__(self, ti, dti, value, dt_clk, chname, group, group_name):
    self.ti = ti
    self.tf = ti + dti
    self.value = value
    self.dt_clk = dt_clk
    self.chname = chname
    self.group = group
    self.group_name = group_name

    # one more check to be sure that dt was big enough
    # we do this comparison with integer values of clocks
    assert dti > 0, 'transition width too small at \n\t{}'.format( self )


  def __cmp__(self, other):
    if self.ti < other.ti and self.tf <= other.ti:
      return -1
    elif other.ti < self.ti and other.tf <= self.ti:
      return 1
    else:
      raise OverlapError(
        'overlapping waveform elements [\n'
        '  {self}\n'
        '  {other}\n'
        ']!'
        .format( self=self, other=other )
      )

  def __repr__(self):
    return '{G}/{C}{group}:(ti={t0}({ti}),tf={t1}({tf}),{v},dt_clk={dt_clk})' \
      .format(
        G=self.group_name, C=self.chname, group=self.group,
        t0=self.ti*self.dt_clk, ti=self.ti,
        t1=self.tf*self.dt_clk, tf=self.tf,
        v=self.value, dt_clk=self.dt_clk,
      )


class ClampedInterp1d:
  def __init__(self, x, y):
    data = list( np.array([x, y]).T )
    data.sort( key = lambda v : v[0] )
    data = np.array(data)
    self.interp = interp1d( data[:,0], data[:,1] )

  def pointwise(self,x):
    if x < self.interp.x[0]:
      return self.interp.y[0]
    elif x > self.interp.x[-1]:
      return self.interp.y[-1]
    else:
      return self.interp(x)

  def __call__(self, xs):
    if np.iterable(xs):
      return np.array( map(self.pointwise, np.array(xs)) )
    else:
      return self.pointwise(xs)


def make_univariate_spline(scaling,units,offset,order=1,smooth=0,
                           globals=globals()):
  # we have to first evaluate everything, build an array, and sort
  L = calculate_scaling(scaling, units, offset, globals)
  mn, mx   = L[0,0], L[-1,0]

  # to make things more natural for the user, we'll first generate a higher
  # resolution interpolation of voltage vs output.  We'll then swap the axes on
  # this higher-resolution data and generate a first order interpolation with no
  # smoothing of output vs voltage.

  # 1.  generate the higher order resolution of voltage vs output
  s = UnivariateSpline(L[:,0], L[:,1], k=order, s=smooth)
  hl = 100.*len(L)

  voltage = np.arange(0.0, hl) * (mx-mn)/(hl - 1.0) + mn
  output = s(voltage)

  # 2.  create a new linear interpolator of output vs voltage
  return ClampedInterp1d( output, voltage )


def set_units_and_scaling(chname, ci, chan, globals):
  if not ci['units']:
    if chan['units']:
      ci['units'] = evalIfNeeded(chan['units'], globals)
    elif ci['type'] is 'analog':
      ci['units'] = unit.V

  if (not ci['scaling']) and chan['scaling']:
    assert ci['units'], chname+': dimensions required for scaling'
    assert chan['interp_order'], \
      chname+': expected interpolation order for scaling'
    assert chan['interp_smoothing']>=0, \
      chname+': expected interpolation smoothing >=0 for scaling'
    ci['scaling'] = make_univariate_spline(
      chan['scaling'],
      ci['units'],
      chan['offset'],
      chan['interp_order'],
      chan['interp_smoothing'],
      globals=globals,
    )



class WaveformEvalulator:
  def __init__(self,devcfg, clocks, channels, globals, continuous):
    # currently configured...
    self.devcfg = devcfg
    self.clocks = clocks
    self.channels = channels
    self.continuous = continuous

    # all the currently known possible channels
    self.timing_channels = backend.get_timing_channels()
    self.do_ao_channels = backend.get_analog_channels()
    self.do_ao_channels.update( backend.get_digital_channels() )

    self.transitions = dict()
    self.explicit_timing = dict()
    self.finite_mode_end_clocks_required = set()
    self.channel_info = make_channel_info(channels)
    self.t_max = 0.0*unit.s
    self.eval_cache = dict()

    debug('compute.waveforms:  initializing channel_info...')
    # initialize the channel info (min period, ...):
    self.min_periods = dict()
    for chname, chan in self.channels.items():
      if not ( chname and chan['enable'] ):
        continue

      ci = self.channel_info[chname]
      # drop the "Analog/" "Digital/" prefix to lookup actual device
      chan_dev = self.do_ao_channels[ chan['device'].partition('/')[-1] ]

      # set type and clock
      ci['type'] = chan_dev.type()
      try:
        clk = self.devcfg[ str(chan_dev.device()) ]['clock']['value']
      except KeyError:
        raise UserWarning( str(chan_dev.device()) + ': Device not configured' )
      assert clk in self.clocks, \
             str(chan_dev.device()) + ': device clock not selected'
      ci['clock'] = clk

      if clk not in self.transitions:
        self.transitions[ clk ] = list()
        self.explicit_timing[ clk ] = False

      # determine if the channel needs explicit timing (in case its clock
      # source is not aperiodic)
      self.explicit_timing[clk] |= chan_dev.explicit_timing()

      # sets ci['units'], ci['scaling'], etc
      # units and scaling only get to refer to globals
      set_units_and_scaling(chname, ci, chan, globals)
      ci['last'] = ci['init'] = evalIfNeeded( chan['value'], globals )

      # in this loop, we first need to determine the largest period required by
      # all devices that share each clock.  In a subsequent loop below, we'll
      # assign this found maximum period required to each of the devices that
      # use a particular clock.
      # project device min_period to the nearest next later clock pulse
      clock_period = self.timing_channels[ clk ] .get_min_period()
      self.min_periods[ clk ] = max(
        self.min_periods.get(clk, clock_period),
        ceil( chan_dev.get_min_period() / clock_period ) * clock_period,
      )

      # check whether channel requires end-clock pulse for non-continuous mode
      if chan_dev.finite_mode_requires_end_clock():
        self.finite_mode_end_clocks_required.add( ci['clock'] )

    debug('compute.waveforms: assigning limiting min_period for each channel...')
    # now we assign the required period to each device that uses each clock
    rem_list = list()
    for chname, ci in self.channel_info.items():
      if ci['clock'] is None:
        rem_list.append( chname )
        continue
      ci['min_period'] = self.min_periods[ ci['clock'] ]
    for i in rem_list:
      self.channel_info.pop(i)


  def group(self, group, t=0*unit.s, dt=0*unit.s, globals=None, locals=dict(),
            name='root'):
    log(DEBUG-1, 'compute.waveforms:  enter group %s', name)
    # natural time for all elements immediately in this group
    t_locals = dict()
    # t is used for calculating natural time 't' for sub-groups
    t_start = t # the start of *this* group

    for gi in group:
      if not gi['enable']:  continue

      # this will allow the sub-group to have t and dt (from its parent) while
      # evaluating its script.  If the sub-group script modifies t or dt, it
      # will only affect that sub-group.
      locals['dt'] = dt

      if 'group-label' in gi:
        # this _must_ be a group, so prepare to recurse
        # 1.  evaluate local script environment
        L = locals.copy()
        L['t'] = t    # natural start time for the sub-group
        if gi['script']:
          exec gi['script'] in globals, L

        # 2.  establish local start time and durations...
        gi_t = evalIfNeeded( gi['time'], globals, L )
        unit.s.unitsMatch(gi_t, gi['group-label']+'(t):  expected dimensions of time')
        assert gi_t >= 0*unit.s, \
          '{G}/{path} (t): MUSt be >= 0!' \
          .format( G=gi['group-label'], path=gi['path'] )

        # sub-group dt defaults to this groups dt
        if not gi['duration']:
          gi_dt = dt
        else:
          gi_dt = evalIfNeeded( gi['duration'], globals, L )
          unit.s.unitsMatch(gi_dt,gi['group-label']+'(dt): expected dimensions of time')
        assert gi_dt >= 0*unit.s, \
          '{G}/{path} (dt): MUST be >= 0!' \
          .format( G=gi['group-label'], path=gi['path'] )
        self.eval_cache[ gi['path'] ] = dict(t=gi_t, dt=gi_dt)

        # 3.  recurse
        self.group( gi['elements'], gi_t, gi_dt, globals, L, gi['group-label'] )

        # 4.  increment natural time for siblings
        if not gi['asynchronous']:
          t = max(t, gi_t+gi_dt)

      else:
        # this _must_ be a waveform element...
        chname = gi['channel']
        if not chname:
          continue # channel for element not selected yet

        try:
          chan = self.channels[chname]
        except:
          raise RuntimeError('Waveform element with non-existent channel: '+chname)
        if not chan['enable']:
          continue # channel not enabled

        if not chan['device']:
          continue # device for channel not yet specified
        # #### END SILENT SKIPPING #### #

        t_locals.setdefault(chname, t_start)
        locals['t'] = t_locals[ chname ]
        t_locals[ chname ] = self.element( name, gi, globals, locals )

    if t_locals:
      self.t_max = max( self.t_max, *t_locals.values() )

    log(DEBUG-1, 'compute.waveforms:  leave group %s', name)


  def element(self, parent, e, globals, locals):
    chname = e['channel']
    err_prefix = '{G}/{C}{P}'.format( G=parent, C=chname, P=e['path'] )
    log(DEBUG-1, 'compute.waveforms:  enter element %s', err_prefix)
    ci = self.channel_info[chname]

    # get a ref to the list of transitions for the associated clock generator
    trans = self.transitions[ ci['clock'] ]

    # provide access to this channels minimum clock period
    dt_clk = ci['min_period']
    locals['dt_clk'] = dt_clk

    # establish local start time / duration for the element
    t = evalIfNeeded( e['time'], globals, locals )
    unit.s.unitsMatch(t, err_prefix+' (t): expected dimensions of time')
    assert t >= 0*unit.s, err_prefix + ' (t): MUSt be >= 0!'

    if not e['duration']:
      dt = locals['dt']
    else:
      dt = evalIfNeeded( e['duration'], globals, locals )
      unit.s.unitsMatch(dt, err_prefix+' (dt): expected dimensions of time')
    assert dt > 0*unit.s,   err_prefix+' (dt): MUSt be > 0!'

    # we're finally to the point to begin evaluating the value of the element
    locals['t'] = t
    locals['dt'] = dt
    value = evalIfNeeded( e['value'], globals, locals )

    # t and dt must be aligned to the nearest clock pulse
    ti  = int( round(       t  / dt_clk ) )
    # create dt to help ensure that it does not overlap with next t
    dti = int( round( (t + dt) / dt_clk ) ) - ti

    log(DEBUG-2, 'compute.waveforms(%s): t=%s, dt=%s, actual: t=%s, dt=%s',
        err_prefix, t, dt, ti*dt_clk, dti*dt_clk )

    if not hasattr( value, 'set_vars' ):
      # we assume that this value is just a simple value
      insert_value(ti, dti, value, dt_clk, chname, ci, trans, e['path'], parent)
      ci['last'] = value
    else:
      debug('%s.set_vars(%s,%s,%s,%s)', value, ci['last'], ti, dti, dt_clk)
      value.set_vars( ci['last'], ti, dti, dt_clk )
      for tij, dtij, v in value:
        insert_value(tij, dtij, v, dt_clk, chname, ci, trans, e['path'], parent)
        ci['last'] = v

    # cache for presentation to user--use integer*dt_clk for accuracy of info
    # do this _after_ inserting value so that functional forms can respond to
    # values as given by <function>.set_vars(...)
    self.eval_cache[ e['path'] ] = \
      dict( t=ti*dt_clk, dt=dti*dt_clk, val=repr(value) )

    locals.pop('dt_clk')
    
    log(DEBUG-1, 'compute.waveforms:  leave element %s', err_prefix)
    # we need to return the end time of this waveform element
    return t + dt


  def finish(self):
    debug('initial t_max: %s', self.t_max)
    # the return values are initially empty
    retvals = {'analog':dict(), 'digital':dict()}
    clocks  = dict()

    t_max = self.t_max
    for chname, ci in self.channel_info.items():
      if not ci['type']:
        continue # not enabled

      prfx, dev = prefix(self.channels[ chname ]['device'])

      D = retvals.get( ci['type'], None )
      if D is None:
        raise RuntimeError("type of channel '"+chname+"' reset?!")

      elems = ci['elements']
      trans = self.transitions[ ci['clock'] ]
      dt_clk = ci['min_period']
      if len(elems) == 0 or elems[0].ti > 0:
        # first element of this channel is at t > 0 so we insert a
        # t=0 value that lasts for at least t_clk time
        insert_value(0,1, ci['init'], dt_clk, chname, ci, trans, (-1,),'root')
      if not self.continuous:
        insert_value( int(round( self.t_max / dt_clk )), 1, ci['init'],
                      dt_clk, chname, ci, trans,
                      (sys.maxint,), 'root' )
        t_max = max( t_max, t_max + dt_clk )

      if prfx not in D:
        D[ prfx ] = dict()
      D[ prfx ][ dev ] = to_plottable( elems )
      clocks[ dev ] = dt_clk

    self.t_max = t_max
    debug('final t_max: %s', self.t_max)

    # ensure that we have a unique set of transitions
    clock_transitions = dict()
    for i in self.transitions:
      if self.timing_channels[i].is_aperiodic() or not self.explicit_timing[i]:
        self.transitions[i] = set( self.transitions[i] )
      else:
        self.transitions[i] = xrange( 0, max(self.transitions[i]) + 1 )

      clock_transitions[i] = dict(
        dt = self.min_periods[i],
        transitions = self.transitions[i],
      )

    return retvals['analog'], retvals['digital'], clock_transitions, clocks, \
           self.t_max.coeff, self.finite_mode_end_clocks_required, \
           self.eval_cache


def insert_value( ti, dti, v, dt_clk, chname, ci, trans, group, group_name ):
  # apply scaling and convert to proper units
  v = apply_scaling(v, chname, ci)
  check_final_units(v, chname, ci)

  u = UniqueElement(ti, dti, v, dt_clk, chname, group, group_name)
  if rootlog.getEffectiveLevel() <= (DEBUG-1):
    log(DEBUG-1, 'inserting transition:\n%s', repr(u) )

  bisect.insort_right( ci['elements'], u )
  trans.append( u.ti )


def waveforms( devcfg, clocks, signals, channels, waveforms, globals,
               continuous=True ):
  """
  Take the configuration as provided by the user and generate a set of waveforms
  that can then be sent to the plotter and/or a hardware driver for output.

  This process is done in two major steps:
    1.  Determine all times that must make a voltage transition on some channel.
    2.  Generate a voltage sample for each transition that must occur.
  """
  wve = WaveformEvalulator(devcfg, clocks, channels, globals=globals,
                           continuous=continuous)
  debug('compute.waveforms: beginning group recursion...')
  wve.group( waveforms, globals=globals )
  debug('finalizing compute.waveforms')
  return wve.finish()


def to_plottable( elem ):
  retval = dict()
  for e in elem:
    if e.group not in retval:
      retval[e.group] = list()
    retval[e.group].append( (e.ti, e.value) )

  return retval



def apply_scaling(value, chname, ci):
  # apply scaling and range checks...
  if not ci['scaling']:
    if ci['units']:
      value *= unit.V / ci['units']
    # else digital required to be boolean
  else:
    assert ci['units'], chname+':  dimensions required for scaling'
    val = value / ci['units']
    assert type(val) is not physical.Quantity, \
      chname+':  wrong units: {}, expected [{}]' \
      .format(value, ci['units'])
    value = ci['scaling'](val)*unit.V

  return value



def make_channel_info(channels):
  D = dict()
  for c in channels:
    D[c] = {
      'type':None,
      'init':None,
      'elements': list(),
      'scaling' : None,
      'units'   : None,
      'last' : None,
      'clock' : None,
      'min_period' : None,
    }
  return D



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



def prefix( devname ):
  # we have to make sure we chop off the 'Analog' and 'Digital' part
  dev = devname.partition('/')[-1]
  return dev.partition('/')[0], dev



def static( devcfg, channels, globals ):
  """
  Take the configuration as provided by the user and generate a set of static
  output values that can then be sent to hardware drivers for output.
  """
  # the return values are initially empty
  analog = dict()
  digital = dict()

  channel_info = make_channel_info(channels)

  for chname in channels:
    ci = channel_info[chname]
    chan = channels[chname]

    if not ( chname and chan['enable'] ):
      continue

    dev = chan['device']
    if not dev:
      continue

    do_ao_channels = backend.get_analog_channels()
    do_ao_channels.update( backend.get_digital_channels() )
    # drop the "Analog/" "Digital/" prefix to lookup actual device
    chan_dev = do_ao_channels[ chan['device'].partition('/')[-1] ]

    # we do most of the same basic things as for waveforms without transitions
    ci['type'] = chan_dev.type()
    set_units_and_scaling(chname, ci, chan, globals)
    value = evalIfNeeded( chan['value'], globals )
    value = apply_scaling(value, chname, ci)
    check_final_units( value, chname, ci )

    prfx, dev = prefix(dev)
    if   ci['type'] is 'analog':
      if prfx not in analog:
        analog[ prfx ] = dict()
      analog[ prfx ][ dev ] = value
    elif ci['type'] is 'digital':
      if prfx not in digital:
        digital[ prfx ] = dict()
      digital[ prfx ][ dev ] = value
    elif not ( ci['type'] ):
      pass
    else:
      raise RuntimeError("type of channel '"+chname+"' reset?!")

  return analog, digital
