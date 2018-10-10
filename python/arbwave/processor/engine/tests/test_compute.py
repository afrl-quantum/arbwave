# vim: ts=2:sw=2:tw=80:nowrap
"""
Test compute(...)
"""

import unittest
from os import path
import copy
from physical import unit

import arbwave.options
import arbwave.backend
from arbwave.processor import default
import arbwave.processor.engine.send as send
from .. import compute

THIS_DIR = path.dirname( __file__ )

# typical import of physical units
physical_import = """\
from physical.constant import *
from physical.unit import *
from physical import unit
"""


def load_config_file():
  simple_config_path = path.join( THIS_DIR, *(
    [path.pardir]*5 + ['examples','simple_config.py']
  ))
  variables = dict()
  exec(compile(open( simple_config_path ).read(), simple_config_path, 'exec'),
       globals(), variables)
  return simple_config_path, variables


def load_simulated_drivers(host_defs):
  arbwave.options.simulated = True
  send.to_driver.hosts( host_defs )

def unload_simulated_drivers():
  arbwave.backend.unload_all()


class ComputeBase(unittest.TestCase):
  def setUp(self):
    # setup global variables
    # we are not yet executing L['global_script'] because I don't want
    # to have to import Arbwave fake module as well (yet).
    self.G = default.get_globals()
    exec(physical_import, self.G)

    self.simple_config_path, self.L = load_config_file()
    load_simulated_drivers(self.L['hosts'])
    send.to_driver.clocks( self.L['clocks'] )
    send.to_driver.config( self.L['devices'], self.L['channels'],
                           self.L['signals'], self.L['clocks'], self.G )
    send.to_driver.signals( self.L['signals'] )

  def tearDown(self):
    unload_simulated_drivers()
    del self.simple_config_path
    del self.L


  static_answer = (
    {'ni': {
      'ni/Dev1/ao0': 10.0 * unit.V,
      'ni/Dev1/ao1': -5.0 * unit.V,
    }},
    {'vp': {
      'vp/Dev0/A/0': False,
    }},
  )
  def test_static(self):
    # setup global variables
    # we are not yet executing L['global_script'] because I don't want
    # to have to import Arbwave fake module as well (yet).
    vals = compute.static( self.L['devices'], self.L['channels'], self.G )

    self.assertEqual(vals,self.static_answer)



  waveform_answer = {
    'continuous' : (
      {'ni': { # analog
        'ni/Dev1/ao0': {
          (-1,): [ (0, 10.0 * unit.V) ],
          ( 1,): [ (16667, 2.0 * unit.V) ],
          ( 2,): [
            (50000, 0.0 * unit.V),
            (50833, 0.4998199928 * unit.V),
            (51666, 0.999639985599 * unit.V),
            (52499, 1.4994599784 * unit.V),
            (53332, 1.9992799712 * unit.V),
            (54165, 2.499099964 * unit.V),
            (54998, 2.9989199568 * unit.V),
            (55831, 3.4987399496 * unit.V),
            (56664, 3.9985599424 * unit.V),
            (57497, 4.4983799352 * unit.V),
            (58330, 4.998199928 * unit.V),
            (59163, 5.4980199208 * unit.V),
            (59996, 5.9978399136 * unit.V),
            (60829, 6.4976599064 * unit.V),
            (61662, 6.9974798992 * unit.V),
            (62495, 7.497299892 * unit.V),
            (63328, 7.9971198848 * unit.V),
            (64161, 8.4969398776 * unit.V),
            (64994, 8.99675987039 * unit.V),
            (65827, 9.49657986319 * unit.V),
            (66660, 9.99639985599 * unit.V),
            (66666, 10.0 * unit.V),
          ],
        },
        'ni/Dev1/ao1': {
          (-1,): [ (0, -5.0 * unit.V) ],
        }
      }},
      {'vp': { # digital
        'vp/Dev0/A/0': {
          (0,): [
            (200000, True),
            (399999, False),
          ],
          (-1,): [ (0, False) ],
        },
      }},
      { # clock_transitions
        'vp/Dev0/A/13': {'dt': 6e-07 * unit.s, 'transitions': set([
          0, 50833, 52499, 54165, 55831, 57497, 59163, 60829, 62495, 64161, 65827,
          16667, 50000, 51666, 53332, 54998, 56664, 58330, 59996, 61662, 63328,
          64994, 66660, 66666,
        ])},
        'vp/Dev0/Internal_XO': {'dt': 5e-08 * unit.s, 'transitions': set([
          0, 200000, 399999,
        ])},
      },
      { # clocks
        'vp/Dev0/A/0': ('vp/Dev0/Internal_XO', 5e-08 * unit.s),
        'ni/Dev1/ao0': ('vp/Dev0/A/13', 6e-07 * unit.s),
        'ni/Dev1/ao1': ('vp/Dev0/A/13', 6e-07 * unit.s),
      },
      0.04*unit.s, # t_max
      { # eval_cache
        (0,): { 'dt': 0.01 * unit.s, 't': 0.01 * unit.s,
                'val': 'pulse(True, False)'},
        (1,): { 'dt': 0.0099996 * unit.s, 't': 0.0100002 * unit.s,
                'val': '<2.0 kg m^2 / A s^3>'},
        (2,): { 'dt': 0.0100002 * unit.s, 't': 0.03 * unit.s,
                'val': 'ramp(10.0*V, 1.0, 20, 0.0*V, None, <0.0100002 s>)'},
      },
    ),



    'non-continuous' : (
      {'ni': { # analog
        'ni/Dev1/ao0': {
          (-1,): [ (0, 10.0 * unit.V) ],
          ( 1,): [ (16667, 2.0 * unit.V) ],
          ( 2,): [
            (50000, 0.0 * unit.V),
            (50833, 0.4998199928 * unit.V),
            (51666, 0.999639985599 * unit.V),
            (52499, 1.4994599784 * unit.V),
            (53332, 1.9992799712 * unit.V),
            (54165, 2.499099964 * unit.V),
            (54998, 2.9989199568 * unit.V),
            (55831, 3.4987399496 * unit.V),
            (56664, 3.9985599424 * unit.V),
            (57497, 4.4983799352 * unit.V),
            (58330, 4.998199928 * unit.V),
            (59163, 5.4980199208 * unit.V),
            (59996, 5.9978399136 * unit.V),
            (60829, 6.4976599064 * unit.V),
            (61662, 6.9974798992 * unit.V),
            (62495, 7.497299892 * unit.V),
            (63328, 7.9971198848 * unit.V),
            (64161, 8.4969398776 * unit.V),
            (64994, 8.99675987039 * unit.V),
            (65827, 9.49657986319 * unit.V),
            (66660, 9.99639985599 * unit.V),
            (66666, 10.0 * unit.V),
          ],
          (-2,): [ (66667, 10.0 * unit.V) ],
        },
        'ni/Dev1/ao1': {
          (-1,): [ (0, -5.0 * unit.V) ],
          (-2,): [ (66667, -5.0 * unit.V) ],
        }
      }},
      {'vp': { # digital
        'vp/Dev0/A/0': {
          (-1,): [ (0, False) ],
          (0,): [
            (200000, True),
            (399999, False),
          ],
          (-2,): [ (800000, False) ],
        },
      }},
      { # clock_transitions
        'vp/Dev0/A/13': {'dt': 6e-07 * unit.s, 'transitions': set([
          0, 50833, 52499, 54165, 55831, 57497, 59163, 60829, 62495, 64161, 65827,
          16667, 50000, 51666, 53332, 54998, 56664, 58330, 59996, 61662, 63328,
          64994, 66660, 66666, 66667, 66668,
        ])},
        'vp/Dev0/Internal_XO': {'dt': 5e-08 * unit.s, 'transitions': set([
          0, 200000, 399999, 800000, 800001,
        ])},
      },
      { # clocks
        'vp/Dev0/A/0': ('vp/Dev0/Internal_XO', 5e-08 * unit.s),
        'ni/Dev1/ao0': ('vp/Dev0/A/13', 6e-07 * unit.s),
        'ni/Dev1/ao1': ('vp/Dev0/A/13', 6e-07 * unit.s),
      },
      0.04000125*unit.s, # t_max
      { # eval_cache
        (0,): { 'dt': 0.01 * unit.s, 't': 0.01 * unit.s,
                'val': 'pulse(True, False)'},
        (1,): { 'dt': 0.0099996 * unit.s, 't': 0.0100002 * unit.s,
                'val': '<2.0 kg m^2 / A s^3>'},
        (2,): { 'dt': 0.0100002 * unit.s, 't': 0.03 * unit.s,
                'val': 'ramp(10.0*V, 1.0, 20, 0.0*V, None, <0.0100002 s>)'},
      },
    ),
  }

  def run_waveforms_test(self, type):
    waveforms = add_waveform_paths(
      self.L['waveforms']['waveforms'][self.L['waveforms']['current_waveform']]
    )

    analog, digital, transitions, dev_clocks, t_max, eval_cache = \
    compute.waveforms(
      self.L['devices'],
      self.L['clocks'],
      self.L['signals'],
      self.L['channels'],
      waveforms,
      self.G, continuous=(type=='continuous') )

    # has some precision problems with comparing.  so we'll compare with textual
    # versions
    self.assertEqual(repr(analog), repr(self.waveform_answer[type][0]))

    self.assertEqual(digital,     self.waveform_answer[type][1])
    self.assertEqual(transitions, self.waveform_answer[type][2])
    self.assertEqual(dev_clocks,  self.waveform_answer[type][3])
    self.assertAlmostEqual(t_max, self.waveform_answer[type][4])

    # has some precision problems with comparing.  so we'll compare with textual
    # versions
    self.assertEqual(repr(eval_cache),  repr(self.waveform_answer[type][5]))


  def test_continuous_waveforms(self):
    self.run_waveforms_test('continuous')

  def test_non_continuous_waveforms(self):
    self.run_waveforms_test('non-continuous')

  def runTest(self):
    """This function does nothing, but is implemented to make debugging tests
    easier"""
    pass



def add_waveform_paths( waveforms, parent_path=() ):
  waveforms = copy.deepcopy( waveforms )
  for sibling_number, wve in zip( range(len(waveforms)), waveforms ):
    current_path = parent_path + (sibling_number,)
    if 'elements' in wve:
      # recurse to elements within group
      add_waveform_paths( wve['elements'], current_path )
    else:
      wve['path'] = current_path
  return waveforms
