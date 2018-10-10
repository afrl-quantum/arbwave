# vim: ts=2:sw=2:tw=80:nowrap
from os import path
from itertools import chain
import numpy as np
import physical

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
  def simple_dict(self):
    return dict( chain(* zip(*self.values())[1] ) )


class SignalsSet(dict):
  def __init__(self, *args, **kwargs):
    super(SignalsSet,self).__init__(*args, **kwargs)
    # ensure that each member of this signal set is all of the Signals class
    for i,v in self.items():
      self[i] = Signals(v)

  def update(self, other=dict(), **kwargs):
    other_ = { k:Signals(v) for k,v in other.items() }
    kwargs_= { k:Signals(v) for k,v in kwargs.items() }
    super(SignalsSet,self).update( other_, **kwargs_ )

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
        open_i  = lambda clk: open(ff.format(clk.replace('/','-')),'w')
        close_i = lambda f:f.close()
        closeall= lambda :None
      else:
        # single filename
        f = open(ff, 'w')
        open_i  = lambda clk: f
        close_i = lambda ignore:None
        closeall= lambda :f.close()

      for clk,I in self.items():
        f = open_i(clk)
        f.write('# All signals for clock:  {}\n'.format(clk))
        f.write('# t\t'+'\t'.join( I['titles'] ) + '\n') # begin with titles
        np.savetxt( f, I['table'] )
        f.write('\n') # end of block
        close_i(f)
      closeall()

  def to_arrays( self, transitions, dev_clocks, channels ):
    names = create_channel_name_map( channels, dev_clocks )

    output = self.SignalsArrays()
    # Each channel that uses a common clock will create values for a single
    # clock-specific array.
    for clk in { n['clk'] for n in names.values() }:
      # all channels that pertain to clk
      L = [ (d,n)  for d,n in names.items()  if n['clk'] == clk ]
      L.sort( key = lambda i: i[1]['order'] ) # sort by channel order
      dt_clk = float(transitions[clk]['dt']) # strip units

      # now we go through each channel and create complete scan table
      TI = [ (t,list()) for t in transitions[clk]['transitions'] ]
      TI.sort( key = lambda x: x[0] ) # sort by clock cycle

      for l in L:
        signals = self[ l[0] ].simple_dict()
        last = 0
        for t,A in TI:
          if t not in signals:  v = last
          else:                 v = last = float(signals[t]) #strip units
          A.append( v )

      # now let's save this into the final output array
      table = np.array( [[i[0]]+i[1] for i in TI] )
      table[:,0] *= dt_clk # scale time by clock rate
      output[clk] = {
        'titles'  : [ i[1]['name'] for i in L ],
        'table'   : table,
      }
    return output






class _FakeStuffCreator(object):
  """
  class to create fake data for testing Signals(Set) classes
  """
  def __init__(self):
    PLOTDIR = path.join( path.dirname( __file__ ), path.pardir, 'gui', 'plotter' )
    import sys
    sys.path.insert( 0, PLOTDIR )
    import digital, analog
    from io import StringIO
    self.StringIO = StringIO
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
    f = self.StringIO()
    A.save( f )
    return f.getvalue()
    


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
    'D' : { ('A/'+k):v  for k,v in analog.items() },
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
      'transitions' : set(chain(*[ [ i[0] for i in chain(*C.values()) ]
                                   for C in digital.values() ] ))
    },
    'A/clock' : {
      'dt'          : 2.4e-6*physical.unit.s,
      'transitions' : set(chain(*[ [ i[0] for i in chain(*C.values()) ]
                                   for C in analog.values() ] ))
    },
  }

if __name__ == '__main__':
  fake = _FakeStuffCreator()
  print(fake.test_gnuplot())
