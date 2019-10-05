#!/usr/bin/env python3
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
This file is not really for a normal package import
"""

from .bbb_pyro import BBB_PYRO_GROUP, format_objectId
import sys, time, threading
import Pyro4

def main(klass, pyro_port=0):
  import argparse, socket

  hostname = socket.gethostname()
  parser = argparse.ArgumentParser()
  parser.add_argument('--hostid', default=hostname,
    help='Specify the hostid label for this BeagleBone Black [Default: {}]'
         .format(hostname))
  parser.add_argument('--replace', action='store_true',
    help='Replace any currently registered instances matching this '
         'hostid/deviceid with this instance.')
  parser.add_argument('--ns', metavar='NAMESERVER[:PORT]',
    help='Specify Pyro nameserver address (in case it cannot be reached by UDP '
         'broadcasts).')
  parser.add_argument('--ns-probe', metavar='PERIOD', default=300, type=float,
    help='The period (in seconds) between probing the nameserver to test if '
         'this daemon is still registered correctly.  If this daemon is not '
         'still registered, we will re-register it.  To disable this probe, '
         'specify the value of --ns-probe as `inf`.')
  parser.add_argument('--bind', metavar='ADDRESS[:PORT]', default='0.0.0.0',
    help='Specify local interface to bind to')
  parser.add_argument('--nop', action='store_true',
    help='A do-nothing command line argument.  Any number can be used.  This '
         ' helps for writing system start scripts (such as with systemd).')
  args = parser.parse_args()

  import Pyro4

  # locate the NS
  try:
    host, port = None, None

    if args.ns:
      host_port = args.ns.split(':')
      host = host_port[0]

      if len(host_port) > 1:
        port = int(host_port[1])

    print('searching for Naming Service...')
    ns = Pyro4.locateNS(host, port)

  except Pyro4.errors.NamingError:
    print('Could not find name server')
    ns = None

  ip_port = args.bind.split(':')
  bind_ip = ip_port[0]
  if len(ip_port) > 1:
    pyro_port = int(ip_port[1])

  daemon = Pyro4.Daemon(host=bind_ip, port=pyro_port)

  device = klass(args.hostid)

  uri = daemon.register(device, device.objectId)
  uri.host = args.hostid

  if ns:
    class NSMonitor(threading.Thread):
      def __init__(self, objectId, uri, safe, ns, period):
        super(NSMonitor, self).__init__()
        self.objectId = objectId
        self.uri = uri
        self.safe = safe
        self.ns = ns
        self.period = period
        self.last_test = -float('inf')
        self.go = True

      def stop(self):
        self.go = False

      def _regerr(self):
        print('could not re-register', self.objectId, 'with nameserver.\n'
              'Will try again in another', self.period, 'seconds')

      def run(self):
        while self.go:
          now = time.time()
          if now - self.last_test > self.period:
            try:
              p = self.ns.lookup(self.objectId)
              if str(p) != self.uri:
                raise Pyro4.errors.NamingError('incorrect URI')
            except (Pyro4.errors.NamingError, Pyro4.errors.ConnectionClosedError):
              try:
                self.ns.register(self.objectId, self.uri, self.safe)
                print('re-registered ', self.objectId, 'with nameserver')
              except Exception as e:
                if not isinstance(e, Pyro4.errors.CommunicationError):
                  print('Unexpected exception in Pyro4 comms: ', e)
                self._regerr()
            except Exception as e:
              if not isinstance(e, Pyro4.errors.CommunicationError):
                print('Unexpected exception in Pyro4 comms: ', e)
              self._regerr()

            self.last_test = now

          if self.period == float('inf'):
            # no need to continue
            return

          time.sleep(self.period)

    nsmonitor = NSMonitor(device.objectId, uri, not args.replace, ns,
                          args.ns_probe)
    nsmonitor.start()

  print('my uri is: ', uri)

  try:
    daemon.requestLoop()
  except:
    if ns:
      nsmonitor.stop()
      nsmonitor.join()
      # try removing self from Pyro name server
      try: ns.remove(device.objectId)
      except Pyro4.errors.NamingError: pass
