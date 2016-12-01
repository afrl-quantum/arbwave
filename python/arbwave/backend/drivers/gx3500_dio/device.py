# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
Logical device driver for GX3500 timing/DIO board.

@author: bks
"""

import copy
import itertools
from logging import debug
import numpy as np
from physical import units
import time

from ...device import Device as Base


_port_bases = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
_group_bases = {'E': 0, 'F': 4, 'G': 8, 'H': 12, 'J': 16, 'K': 20, 'L': 24, 'M': 28}

def _port_bit(path_or_line):
    """
    Convert a path or line number to a (port_nr, bit_nr) bit addess. The
    path should just be the tail port/group#bit part (e.g. A/G2)

    :return: the (port_nr, bit_nr) tuple such that 
             (ports[port_nr] & (1 << bit_nr)) >> bit_nr
             will extract the referenced bit.
    """
    if type(path_or_line) == str:
        assert len(path_or_line) == 4, \
          'Path must be of the form A/E0'
        port_nr = _port_bases[path_or_line[0]]
        bit_nr = _group_bases[path_or_line[2]] + int(path_or_line[3])
    else:
        port_nr = int(path_or_line / 32)
        bit_nr = int(path_or_line % 32)

    return (port_nr, bit_nr)

def _make_instr(dt, new_ports):
    """
    Format a GX3500 instruction.

    :param dt: the instruction duration (in 50 ns units)
    :param new_ports: a sequence of 4 ports, either a bitmask or None

    :return: a sequence of instruction words
    """
    dt_board = 5*(dt - 1) # convert to 10ns units, with '0' == 50 ns
    portmask = 0
    instr = [0]
    for i, mask in enumerate(new_ports):
        if mask is not None:
            portmask |= (1 << (31 - i))
            instr.append(mask)
    instr[0] = dt_board | portmask
    return instr

class Device(Base):
    """
    The logical Device for a single instance of the GX3500 timing/DIO board.
    """

    def __init__(self, driver, address, N, simulated=False):
        """
        Instantiate a Device.
        
        :param address: the board PCI bus/slot address
        :param simulated: if True, use a simulated version of the timing board
        """
        super(Device,self).__init__(name='{}/Dev{}'.format( driver, N ))
        self.driver = driver

        if not simulated:
            from marvin import timingboard
            self.board = timingboard.TimingBoard(address)
        else:
            from marvin import timingboard_sim
            self.board = timingboard_sim.TimingBoard(address)

        self.possible_clock_sources = [
            '{dev}/Internal_PXI_10_MHz'.format(dev=self),
            '{dev}/Internal_XO'.format(dev=self)
        ]

        self.config = self.get_config_template()

        self.clocks = None
        self.signals = None
        self.is_continuous = False
        self.ports = np.zeros((4,), dtype=np.uint32)
        self.set_output({}) # write the port values to the hardware

    def __del__(self):
      self.close()

    def close(self):
        """
        Final cleanup.
        """
        if hasattr(self, 'board'):
            self.board.command('STOP')

    def get_config_template(self):
        """
        Create the configuration template (the set of possible configuration
        parameters and their allowed values).

        :return: the configuration template
        """
        return {
            'clock': {
                'value': '',
                'type': str,
                'range': self.possible_clock_sources
            },
            'trigger': {
                'enable': {
                    'value': False,
                    'type': bool,
                    'range': None
                },
                'invert': {
                    'value': False,
                    'type': bool,
                    'range': None
                },
                'mode' : {
                    'value' : 'edge',
                    'type' : str,
                    'range' : [
                        ('edge', 'Trigger on Rising/Falling Edge of Trigger'),
                        ('level','Trigger on Level of Trigger'),
                    ],
                },
            },
        }

    def set_config(self, config):
        """
        Set the internal configuration for the board. This
        does not include the sequence specification or the PXI routing.

        :param config: the configuration dictionary to be applied, compare
                       get_config_template()
        """
        debug('gx3500.Device({}).set_config(config={})'.format(self, config))
        valid_keys = set(self.get_config_template().keys())
        assert set(config.keys()).issubset(valid_keys), \
          'Unknown configuration keys for GX3500 timing board'

        if self.config == config:
            return

        self.config = copy.deepcopy(config)

    def set_clocks(self, clocks):
        """
        Set which clock is controlling the board.

        :param clocks: a dict of {'clock/path': config_dict }
        """
        debug('gx3500.Device({}).set_clocks(clocks={})'.format(self, clocks))
        if self.clocks == clocks:
            return
        self.clocks = copy.deepcopy(clocks)
        # FIXME: do we need to do anything else here?

    def set_signals(self, signals):
        """
        Set the PXI routing bits.

        :param signals: a dict of { (src, dest) : config_dict} where src and
                        dest are both paths
        """
        debug('gx3500.Device({}).set_signals(signals={})'.format(self, signals))
        if self.signals == signals:
            return
        self.signals = copy.deepcopy(signals)

        skip_self = len(str(self)) + 1

        kwroutes = {}
        used_triggers = set()

        for src, dest in signals.iterkeys():
            if src.startswith( str(self) ) and 'TRIG' in dest:
                n = int(dest[-1])
                if n < 0 or n > 7:
                    raise ValueError('cannot route to ' + dest)
                if n in used_triggers:
                    raise ValueError('cannot route multiple channels to ' + dest)
                used_triggers.add(n)

                port, bit = _port_bit(src[skip_self:])
                kwroutes['pxi' + dest[-1]] = 32*port + bit

        debug('gx3500.Device({}): calling board.set_pxi_routing(**{})' \
               .format(self, kwroutes))
        self.board.set_pxi_routing(**kwroutes)

    def set_output(self, values):
        """
        Immediately force the output on several channels; all others are
        unchanged. Channels default to LOW on board initialization.

        :param values: the channels to set. May be a dict of { <channel>: bool},
                       or a list of [ (<channel>, bool), ...] tuples or something
                       equivalently coercable to a dict

        Channel names can be of the following forms:
          integer:
            between 0 and 127
          'port/group#line':
            port is one of [ABCD]; group is one of [EFGHJKLM],
            and line is between 0 and 3 (e.g. A/E2)
        """
        debug('gx3500.Device({}).set_output(values={})'.format(self, values))
        if not isinstance(values, dict):
            values = dict(values)

        for channel, val in values.iteritems():
            (port, bit) = _port_bit(channel)
            if val:
                self.ports[port] |= (1 << bit)
            else:
                self.ports[port] &= ~(1 << bit)

        debug('gx3500.Device({}): calling board.set_defaults(*{})' \
               .format(self, self.ports))
        self.board.set_defaults(*self.ports)

    def _compile_transition_map(self, waveforms, clock_transitions, t_max):
        """
        Convert the input waveforms from being channel-indexed to being
        timestamp-indexed.

        :param waveforms: the dict of waveforms from the processor engine
        :param clock_transitions: the dict of required clock transitions from the
                                  processor engine
        :param t_max: the total duration of the sequence

        :return: a dict(timestamp: {channel: value})
        """
        debug('gx3500: compiling transitions for {} channels and {} clocks' \
              .format(len(waveforms), len(clock_transitions)))

        transition_map = {}

#        debug('gx3500: input waveforms are \n' + str(waveforms))
        # first reformat the waveforms: this is straightforward
        for channel, groups in waveforms.iteritems():
            for _, transitions in groups.iteritems():
                for timestamp, value in transitions:
                    transition_map.setdefault(timestamp, {})[channel] = value

        # then add the clock transitions
        for channel, cfg in clock_transitions.iteritems():
            if 'Internal' in channel:
                continue

            # calculate the number of 50ns units 
            period = int(round(cfg['dt'] * 20e6 / units.s))
            for edge in cfg['transitions']:
                edge *= period # rescale from dt to 50ns units

                # add clock edges to the transtion map
                # FIXME: it would not be too hard to support inverted channels...
                transition_map.setdefault(edge, {})[channel] = True
                transition_map.setdefault(edge + period/2, {})[channel] = False

        # add a dummy transition to the end to finish the sequence
        ts_max = int(round(t_max * 20e6 / units.s)) # convert to 50ns units
        ts_max = max([max(transition_map.iterkeys())+1, ts_max])
        transition_map[ts_max] = {}

        return transition_map

    def _compile_transitions(self, transition_map):
        """
        Compile the transition map from a dict from timestamps to
        channel values to an ordered list of timestamps and port masks.

        Note that this captures the current manual settings for all channels
        that are not controlled by the waveform specification. If the manual
        value changes the sequence must be recompiled to preserve the new
        manual value.

        :param transition_map: a dict(timestamp: {channel: value})
        :return: a list of tuple(timestamp, port_vals[4])
        """

        # sort and format the transitions
        transitions = []
        ports = np.array(self.ports, copy=True)
        for timestamp in sorted(transition_map.keys()):
            for channel, value in transition_map[timestamp].iteritems():
                port, bit = _port_bit(channel)
                if value:
                    ports[port] |= (1 << bit)
                else:
                    ports[port] &= ~(1 << bit)
            transitions.append((timestamp, np.array(ports, copy=True)))

        return transitions

    def _assemble_program(self, transitions):
        """
        Convert a transition list into a board program for the GX3500. This
        function implements program compression using the port mask bits in the
        hardware instruction format.

        :param transitions: a list of sequence(timestamp, port_vals[4])

        :return: a list of instruction word tuples
        """
        debug('gx3500: assembling a program with {} transitions'.format(len(transitions)))
        instr_list = []
        ports = new_ports = transitions[0][1] # the first instruction writes all 4 ports
        t_last = 0

        # the card only accepts delays of <= 2**28 * 10 ns + 50 ns; we avoid
        # hitting the absolute maximum
        MAX_DURATION = int(2**28/5)

        for timestamp, port_vals in transitions[1:]:
            # figure out the duration and store the previous instruction
            dt = timestamp - t_last
            t_last = timestamp
            nr_hold_instrs = 0
            while dt >= MAX_DURATION:
                # will need to insert zero port mask instructions to hold the port values
                nr_hold_instrs += 1
                dt -= MAX_DURATION - 1
            # store the main instruction
            instr_list.append(_make_instr(dt, new_ports))
            # and then store the additional hold instructions
            for _ in xrange(nr_hold_instrs):
                instr_list.append(_make_instr(MAX_DURATION - 1, [None]*4))

            # then figure out which ports have changed for the next instruction
            new_ports = [ new if new != old else None for new, old in zip(port_vals, ports)]
            ports = port_vals

        # note that the last "transition" never gets executed: it only
        # specifies the duration of the next-to-last
        return instr_list

    def _upload_program(self, instr_list):
        """
        Upload a compiled program to the GX3500 board.

        :param instr_list: the list of instruction word tuples
        """
        if len(instr_list) == 0:
            raise ValueError('gx3500: cannot upload zero-length program')

        words = np.fromiter(itertools.chain(*instr_list), dtype=np.uint32)
        if len(words) >= 2**16 - 1:
            raise ValueError('gx3500({}): program too long'.format(self))

        debug('gx3500: uploading a program of {} words'.format(len(words)))
        program_dump = np.array2string(words, max_line_width=78,
                                       formatter={'all': lambda v: hex(v)[:-1]})
#        debug('gx3500({}): program dump follows:\n'.format(self) + program_dump)
        self.board.write('mem', 0x0000, words)

    def set_waveforms(self, waveforms, clock_transitions, t_max, continuous):
        """
        Set the output waveforms for the GX3500 device.

        :param waveforms: a dict('channel': {'group': [(t1, val1), (t2, val2)]})
                          (see gui/plotter/digital.py for format)
        :param clock_transitions: a dict('channel': { 'dt': dt, 
                                  'transitions': iterable})
                                  (see processor/engine/compute.py for format)
        :param t_max: the maximum duration of any channel
        :param continuous: bool of continuous or single-shot mode
        """

        if set(waveforms.iterkeys()).intersection(clock_transitions.iterkeys()):
            raise RuntimeError('GX3500 channels cannot be used as clocks and ' \
                               'digital output simultaneously')

        # remove Internal clocks from the clock_transitions
        clock_transitions = { c:p for c, p in clock_transitions.iteritems()
                              if 'Internal' not in c }
#        debug('gx3500: clock transitions for {}'.format(clock_transitions))

        assert set([str(self) + '/' + c for c in clock_transitions]) \
                 .issubset(self.clocks.iterkeys()), \
            'got clock transitions for channels not defined as clocks'

        transition_map = self._compile_transition_map(waveforms, clock_transitions, t_max)
        transitions = self._compile_transitions(transition_map)
        instr_list = self._assemble_program(transitions)

        self._upload_program(instr_list)

        self.board.config(
          number_transitions      =len(instr_list),
          repetitions             =0 if continuous else 1,
          use_10_MHz              =not 'Internal_XO' in self.config['clock']['value'],
          external_trigger        =self.config['trigger']['enable']['value'],
          invert_external_trigger =self.config['trigger']['invert']['value'],
          external_trigger_type   =self.config['trigger']['mode']['value'],
          auto_trigger            =not self.config['trigger']['enable']['value'],
        )

        self.is_continuous = continuous

    def start(self):
        """
        Start the sequence: arm the board, and trigger if it is not waiting
        for a hardware trigger.
        """
        # force all the clock channels to LOW in preparation but don't change
        # the manual preset values
        p = np.array(self.ports, copy=True)
        pfxlen = len(str(self)) + 1
        clock_channels = { c[pfxlen:]: False for c in self.clocks if 'Internal' not in c}
        self.set_output(clock_channels)
        self.ports = p

        # arm the board; if it not expecting a hardware trigger, sequencing will
        # automatically start (see auto_trigger above)
        debug('gx3500: ARMing the board')
        self.board.command('ARM')

    def wait(self):
        """
        Wait for the sequence to finish.
        """
        if self.is_continuous:
            raise RuntimeError('cannot wait for continuous waveform to finish')

        while self.board.state != 'SETUP':
            time.sleep(0.1)
#            debug('gx3500: waiting, board is in ' + self.board.state)

    def stop(self):
        """
        Forceably stop any running sequence.
        """
        try:
            # work even on uninitialized Devices
            self.board.command('STOP')
        except AttributeError:
            pass
