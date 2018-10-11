#!/usr/bin/env python
# vim: ts=2:sw=2:tw=80:nowrap
# -*- coding: utf-8 -*-
"""
This file is not really for a normal package import
"""

from .bbb_pyro import BBB_PYRO_GROUP, format_objectId
import sys
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

    #bind_ip = ns._pyroConnection.sock.getsockname()[0]
  except Pyro4.errors.NamingError:
    print('Could not find name server')
    ns = None
    #bind_ip = args.hostid

  bind_ip = '0.0.0.0'
  daemon = Pyro4.Daemon(host=bind_ip, port=pyro_port)

  device = klass(args.hostid)

  uri = daemon.register(device, device.objectId)
  uri.host = args.hostid

  if ns:
    ns.register(device.objectId, uri, safe=not args.replace)
  print('my uri is: ', uri)

  try:
    daemon.requestLoop()
  except:
    if ns:
      # try removing self from Pyro name server
      try: ns.remove(device.objectId)
      except Pyro4.errors.NamingError: pass
