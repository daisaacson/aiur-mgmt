#!/usr/bin/env python

import base64, re
from optparse import OptionParser
import sys

def enc():
  if options.verbose: print "encode() " + args[0]
  print base64.b64encode(args[0])

def dec():
  if options.verbose: print "decode() " + args[0]
  print base64.b64decode(args[0])

def isBase64(s):
  return (len(s) % 4 == 0) and re.match('^[A-Za-z0-9+/]+[=]{0,2}$', s)

def main():
  if options.encode:
    enc()
  elif options.decode or isBase64(args[0]):
    dec()
  else:
    print "error"

if __name__ == '__main__':
  description = "Decode/Encode base64"
  epilog = "Decode and Encode base64 strings"
  usage = "usage: %prog [options]"
  parser = OptionParser(usage=usage, description=description, epilog=epilog)
  parser.add_option("-d", "--decode", action="store_true", default=True, help="Decode a base64 string")
  parser.add_option("-e", "--encode", action="store_true", help="Encode a base64 string from stdin")
  parser.add_option("-v", "--verbose", action="store_true", help="Verbose")
  (options, args) = parser.parse_args()
  if options.verbose: print "options " + str(options)
  if options.verbose: print "args " + str(args)
  if not len(args) == 1: print "error"
  sys.exit(main())
