# vim: ts=2:sw=2:tw=80:nowrap

from common import *
import physical

def waveforms( channels, waveforms, signals, globals=None ):
  exec global_load

  analog = None
  digital = None

  t = 0*physical.unit.ms
  for group in waveforms:
    L = dict()
    if group['script']:
      exec group['script'] in globals, L

    L['t'] = t
    t_start = eval( group['time'], globals, L )
    try:    dt,  sub_dt = eval( group['duration'], globals, L )
    except: dt = sub_dt = eval( group['duration'], globals, L )
    L['dt'] = dt
    L['sub_dt'] = sub_dt

    print '(t_start,t_end): ', t_start, t_start + dt

    if not dt:
      # each waveform element _must_ have its own duration
      pass
    else:
      # we use the group dt as the default for waveform elements as well as the
      # group duration that goes into calculating the natural time 't' for the
      # next group
      pass

    if not group['asynchronous']:
      t = t_start + dt

  return analog, digital
