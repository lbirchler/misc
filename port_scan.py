#!/usr/bin/env python3
"""
fast port scanner
example: ./port_scan.py 192.168.0.0/24 22
"""
import errno
import ipaddress
import os
import socket
import sys


def fatal(msg):
  print(msg, file=sys.stderr)
  sys.exit(1)


def main():
  if len(sys.argv) != 3:
    fatal("usage: %s IP/CIDR PORT" % sys.argv[0])
  
  try:
    ip_net = ipaddress.ip_network(sys.argv[1])
  except:
    fatal("error: bad ip/cidr")
  
  port = int(sys.argv[2])
  if not (1 <= port <= 65535):
    fatal("error: bad port")
  
  ips = [ip for ip in ip_net][1:-1]
  print('scanning from %s to %s on port %d' % (str(ips[0]), str(ips[-1]), port), file=sys.stderr)

  for ip in ips:
    if not os.fork():
      status = ""
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
      s.settimeout(0.1)
      rc = s.connect_ex((str(ip), port))
      s.close()
      if rc == 0:
        status = "open"
      elif rc == errno.ECONNREFUSED:
        status = "closed"
      if status:
        print("%-15s %s" % (str(ip), status))
      os._exit(0)

  while True:
    try:
      os.wait()
    except ChildProcessError:
      break


if __name__ == "__main__":
    main()
