# vim: ts=2:sw=2:tw=80:nowrap
from os import path
from itertools import chain
import numpy as np
import physical

from .dict import Dict

def merge_signals_sets( dev_signals ):
  # take components of device-categorized dictionaries to
  D = SignalsSet()
  for ds in dev_signals:
    for s in ds.values():
      D.update( s )
  return D

def create_channel_name_map(channels, clocks):
  # we need a map from device-name to (channel name,order)
  names = dict()
  for c in channels.items():
    dev = c[1]['device']
    if not dev:
      continue

    if dev and c[1]['enable']:
      if dev in names:
        raise NameError('Device channels can only be used once')
      clk = clocks[dev]
      names[ dev ] = dict( name=c[0], order=c[1]['order'],
                           clk=clk[0], dt_clk=clk[1] )
  return names

class Signals(dict):
  """
  This dictionary instance converts the dictionaries of timing/encoding groups,
  where the group label/id is the key to a dictionary of nearly the same, only
  where the first dt_clk step is the key.

  The data is also transitioned from an array of (time,value) pairs to a
  dictionary of time:value items.
  """
  def __init__(self, *args, **kwargs):
    super(Signals,self).__init__(self._reformat(*args, **kwargs))

  def update(self, *args, **kwargs):
    super(Signals,self).update(self._reformat(*args, **kwargs))

  @staticmethod
  def _reformat(*args, **kwargs):
    D = dict(*args, **kwargs)

    retval = dict()
    return {
      data[0][0]: Dict(
        encoding=enc or 'step', # in case it is *None*
        times = tuple(t for t,val in data),
        data  = dict(data),
      ) for grp, (enc,data) in D.items()
    }


class SignalsSet(dict):
  class SignalsArrays(dict):
    def save( self, ff ):
      # get the handle to an open file
      if type(ff) is not str and hasattr(ff, 'write'):
        # file is already open
        f = ff
        open_i  = lambda clk: f
        close_i = lambda ignore:None
        closeall= lambda :None
      elif '{}' in ff:
        # filename is series format
        open_i  = lambda clk: open(ff.format(clk.replace('/','-')),'wb')
        close_i = lambda f:f.close()
        closeall= lambda :None
      else:
        # single filename
        f = open(ff, 'wb')
        open_i  = lambda clk: f
        close_i = lambda ignore:None
        closeall= lambda :f.close()

      for clk,I in sorted(self.items()): # sorted for consistency/testing
        f = open_i(clk)
        f.write('# All signals for clock:  {}\n'.format(clk).encode())
        f.write(('# t\t'+'\t'.join( I['titles'] ) + '\n').encode()) # begin with titles
        np.savetxt( f, I['table'] )
        f.write(b'\n\n') # end of block
        close_i(f)
      closeall()

  def to_arrays( self, transitions, dev_clocks, channels ):
    names = create_channel_name_map( channels, dev_clocks )

    cache = {k: Signals(v) for k,v in self.items()}

    output = self.SignalsArrays()
    # Each channel that uses a common clock will create values for a single
    # clock-specific array.
    for clk in { n['clk'] for n in names.values() }:
      # all channels that pertain to clk
      chans_w_clk = [ (d,n)  for d,n in names.items()  if n['clk'] == clk ]
      chans_w_clk.sort( key = lambda i: i[1]['order'] ) # sort by channel order
      dt_clk = float(transitions[clk]['dt']) # strip units

      # now we go through each channel and create complete scan table
      TI = [ (t,list()) for t in transitions[clk]['transitions'] ]
      TI.sort( key = lambda x: x[0] ) # sort by clock cycle

      for chname, chinfo in chans_w_clk:
        signals = cache[ chname ]
        grp = Dict(encoding='step', data=dict(), times=(-1,))
        value = 0
        i_tv = -1 # only really used for 'linear' (, 'bezier'?)

        for t,A in TI:
          if t in signals:
            # get new group data
            grp     = signals[t]
            value   = float(grp.data[t])
            i_tv = 0 # the first time for the group

          elif t > grp.times[-1]:
            # beyond the last seen group; output remains fixed
            pass

          elif grp.encoding == 'step':
            # in middle of executing 'step' encoding group
            if t in grp.data:
              value = grp.data[t]
            else:
              # Not at the next step; output remains fixed
              pass

          elif grp.encoding == 'linear':
            # in middle of executing 'linear' encoding group
            if t in grp.data:
              value   = grp.data[t]
              i_tv = grp.times.index(t)
            else:
              # we finally have to do a little bit of interpolation
              # i_tv *must* necessarily be less than (len(grp.times)-1)
              ti = grp.times[i_tv]
              tf = grp.times[i_tv+1]
              di = grp.data[ti]
              value = di + (grp.data[tf] - di) / (tf - ti) * (t - ti)

          else:
            raise RuntimeError(
              'Unkown encoding in flattening output: ' + grp.encoding)

          A.append( value )

      # now let's save this into the final output array; time is first column
      table = np.array( [[t]+A for t, A in TI] )
      table[:,0] *= dt_clk # scale time by clock rate
      output[clk] = {
        'titles'  : [ chinfo['name'] for chname, chinfo in chans_w_clk ],
        'table'   : table,
      }
    return output






class _FakeStuffCreator(object):
  """
  class to create fake data for testing Signals(Set) classes
  """
  def __init__(self):
    from ..gui.plotter import digital, analog
    from io import BytesIO
    self.BytesIO = BytesIO
    self.mod_D, self.mod_A = digital, analog
    D, A = self.mod_D.example_signals, self.mod_A.example_signals
    self.channels = _create_fake_channels( D, A )
    self.signals = _create_fake_signals(D, A)
    self.clocks = _create_fake_dev_clocks(D, A)
    self.transitions = _create_fake_transitions(D, A)

  def print_fake_stuff(self):
    print('type: ', type(self.signals))
    print('clocks: ', self.clocks)
    print('channels: ', self.channels)
    print('transitions: ', self.transitions)
    print('name_map: ', create_channel_name_map(self.channels, self.clocks))
    A = self.signals.to_arrays(self.transitions, self.clocks, self.channels)
    print('array:\n', A)

  def test_gnuplot(self):
    A = self.signals.to_arrays(self.transitions, self.clocks, self.channels)
    f = self.BytesIO()
    A.save( f )
    return f.getvalue().decode()
    


def _create_fake_channels(digital, analog):
  def Order():
    i = 0
    while True:
      yield i
      i += 1
  o = Order()
  channels = {
    ('Digital '+k) : dict( device='D/'+k, enable=True, order=next(o) )
    for k in digital
  }
  channels.update({
    ('Analog '+k) : dict( device='A/'+k, enable=True, order=next(o) )
    for k in analog
  })
  return channels


def _create_fake_signals(digital, analog):
  D = {
    'D' : { ('D/'+k):v  for k,v in digital.items() },
  }
  A = {
    'A' : { ('A/'+k):v  for k,v in analog.items() },
  }
  return merge_signals_sets( [D, A] )

def _create_fake_dev_clocks(digital, analog):
  A_clocks = {('D/'+k) : ('D/clock', 5e-8*physical.unit.s)  for k in digital}
  D_clocks = {('A/'+k) : ('A/clock', 2.4e-6*physical.unit.s)  for k in analog}
  return dict( A_clocks, **D_clocks )

def _create_fake_transitions(digital, analog):
  return {
    'D/clock' : {
      'dt'          : 5e-8*physical.unit.s,
      'transitions' : set([
        t for t, val in chain.from_iterable([
          vals for encoding, vals in chain.from_iterable([
            C.values() for C in digital.values()])])]),
    },
    'A/clock' : {
      'dt'          : 2.4e-6*physical.unit.s,
      'transitions' : set([
        t for t, val in chain.from_iterable([
          vals for encoding, vals in chain.from_iterable([
            C.values() for C in analog.values()])])]),
    },
  }

def test_gnuplot():
  fake = _FakeStuffCreator()
  return fake.test_gnuplot().decode()
