#!/usr/bin/env python
__version__ = 0.1

import os, sys, re, socket
from datetime import datetime
from optparse import OptionParser, OptionGroup
from subprocess import Popen, PIPE, STDOUT

class Ssl:
  def __init__(self, x509, file, index):
    self.x509 = x509                    # PEM, base64 encoded ASCII
    self.file = file                    # Name of file x509 was found in
    self.index = index                  # What number x509 is in file with multiple certs. i.e. ca bundle
    # We process based on EndDate a lot, multiple times per cert. Get it in memory, to prevent lots of calls to the function.
    self.enddate = self.getEndDate()    # Datetime when certifiate expires
    # Don't process everyone's subject or cn. It's a waste of time, if only a fraction of the certs will require this data.
    #self.subject = self.getSubject()
    #self.cn = self.getCN()
  def __repr__(self):
    return self.getCN() + "@" + self.file + "[" + str(self.index) + "]"
  def __lt__(self, other):
    return self.getTimeToExpire() < other.getTimeToExpire()
  def getSubject(self):
    p = Popen(["openssl", "x509", "-noout", "-subject"], stdout=PIPE, stdin=PIPE)
    return self.cleanOutput(p.communicate(input=self.x509.encode())[0])
  def getCN(self):
    c = re.search(r'/CN=([^/$]*)', self.getSubject())
    if c: return c.group(1)
    return self.getSubject()
  def getStartDate(self):
    p = Popen(["openssl", "x509", "-noout", "-startdate"], stdout=PIPE, stdin=PIPE)
    return self.cleanDate(p.communicate(input=self.x509.encode())[0])
  def getEndDate(self):
    p = Popen(["openssl", "x509", "-noout", "-enddate"], stdout=PIPE, stdin=PIPE)
    return self.cleanDate(p.communicate(input=self.x509.encode())[0])
  def getTimeToExpire(self):
    return self.enddate - datetime.now()
  def isValid(self):
    return datetime.now() < self.enddate
  def isExpired(self):
    return not self.isValid()
  def cleanDate(self, datestr):
    # Bug: Not TZ aware
    fmt = "%b %d %H:%M:%S %Y %Z"
    return datetime.strptime(self.cleanOutput(datestr), fmt)
  def cleanOutput(self, output):
    if isinstance(output, bytes):
        output = output.decode()
    return str(output[(output.index('=')+1):]).strip()

def main():
  files = []            # list of files to process
  certs = []            # list of certificates found
  retval = 0            # exit code
  if options.debug: print ("in main()")

  if options.file or options.directory: 
    getFiles(files)
    for file in files:
      certs += [ Ssl(crt, file, idx) for idx, crt in enumerate(processFile(file)) ]

    if options.verbose or options.debug:
      for cert in certs:
        if options.verbose: print (cert.file + "[" + str(cert.index) + "]: " + str(cert.getTimeToExpire().days) + " " + cert.getCN())
        if options.debug: print (cert.x509)

    if options.orion:
      certsExpired = []           # all expired certificates
      certsUnexpired = []         # all unexpired certificates
      certsUnverified = []        # all certificates with broken chains
      orionProcess(certs, certsExpired, certsUnexpired)
      if len(certsExpired) > 0: retval = 3
      certsExpired.sort()
      certsUnexpired.sort()
      orionPrint(certsExpired, certsUnexpired)

  if options.scan:
    print ("scanning...")
    print (socket.gethostbyname(socket.gethostname()))

  return retval

def getLocalIPs():
  localIPs = []

  return localIPs


def getFiles(i):
  if options.directory:
    for d in options.directory:
      if options.verbose: print ("processing dir: " + d)
      for root, subFolders, files in os.walk(d, followlinks=False):
        if options.exclude:
          for exclude in options.exclude:
            if exclude in subFolders: subFolders.remove(exclude)
            if exclude in files: files.remove(exclude)
        for file in files:
          i.append(os.path.join(root,file))

  if options.file:
    if options.exclude:
      for exclude in options.exclude:
        if exclude in options.file: options.file.remove(exclude)
    for f in options.file:
      i.append(f)

def orionPrint(e, u, b=None):
  print ("Statistic.Certs: " + str(len(e) + len(u)))
  print ("Statistic.ExpiredCerts: " + str(len(e)))
  print ("Message.ExpiredCerts: " + str(e))
  if len(u) > 0:
    if options.within > 0:
      w = []
      for c in u:
        if c.getTimeToExpire().days <= options.within: w.append(c)
      print ("Statistic.ExpiringCerts: " + str(len(w)))
      print ("Message.ExpiringCerts: " + str(w) + " will expire within " + str(options.within) + " days")
    else:
      print ("Statistic.ExpiringCerts: -1")
      print ("Message.ExpiringCerts: No certs expiring within " + str(options.within) + " days")
    print ("Statistic.DaysUntilNextExpiration: " + str(u[0].getTimeToExpire().days))
    print ("Message.DaysUntilNextExpiration: " + str(u[0]))
  elif len(u) == 0 and len(e) == 0:
    print ("Statistic.ExpiringCerts: 0")
    print ("Message.ExpiringCerts: No certs found.")
  else:
    print ("Statistic.ExpiringCerts: -1")
    print ("Message.ExpiringCerts: All certs are expired!")
    print ("Statistic.DaysUntilNextExpiration: -1")
    print ("Message.DaysUntilNextExpiration: All certs are expired!")
  if not b is None and not (options.file or options.directory):
    if len(b) > 0:
      print ("Statistic.UnverifiedCerts: " + str(len(b)))
      print ("Message.UnverifiedCerts: " + str(b))
    else:
      print ("Statistic.UnverifiedCerts: -1")
      print ("Message.UnverifiedCerts: All certs chains are tested")
  if options.debug_orion:
    print ("Expired Certificates:")
    for c in e: print (c.getTimeToExpire().days, c)
    print ("Unexpired Certificates:")
    for c in u: print (c.getTimeToExpire().days, c)
    print ("Bad Certificate Chains:")
    for c in b: print (c)
  return 0

def orionProcess(c, e, u):
  for i in c:
    if options.debug_orion or options.debug: print ("orionProcess(): " + str(i.getSubject()))
    if i.isValid():
      if options.debug_orion or options.debug: print ("orionProcess(): " + str(i.isValid()))
      u.append(i)
    else:
      if options.debug_orion or options.debug: print ("orionProcess(): " +str(i.isValid()))
      e.append(i)
  if options.verbose or ( options.debug_orion or options.debug): print ("orionProcess():", str(len(c)), str(len(u)), str(len(e)))

def processFile(f):
  'Return a list of Certificate Blocks from an input file'
  if options.debug: print ("in processFile()")
  if options.verbose: print ("processing file: " + f)
  filecontents = open(f).read()
  if options.debug: print ("filehandle: " + filecontents)
  c = re.findall("(-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----)", filecontents, re.DOTALL)
  if options.debug: print ("  certs: " + str(c))
  if options.verbose: print ("count: " + str(len(c)))
  return c

if __name__ == '__main__':
  description = "Parse SSLs"
  usage = "usage: %prog [options]"
  version = "%prog " + str(__version__)
  parser = OptionParser(usage=usage, description=description, version=version)
  if sys.hexversion >= 33949424: # 2.6
    epilog = "A Suite of tools to Parse SSL files / directories for information"
    parser = OptionParser(usage=usage, description=description, epilog=epilog, version=version)
  else:
    parser = OptionParser(usage=usage, description=description, version=version)
  parser.add_option("-o", "--orion", action="store_true", help="Print Orion Component Output")
  parser.add_option("-v", "--verbose", action="store_true")
  group = OptionGroup(parser, "Orion Computer Scan Options")
  group.add_option("-d", "--directory", "--dir", action="append", help="Directory to search for SSLs")
  group.add_option("-f", "--file", action="append", help="File to parse")
  group.add_option("-x", "--exclude", action="append", help="File or directory to exclude")
  group.add_option("-w", "--within", type=int, default=0, help="print certs that expire within X days")
  parser.add_option_group(group)
  group = OptionGroup(parser, "Port Scan Option")
  group.add_option("-s", "--scan", action="store_true", help="Scan ports for valid chain")
  parser.add_option_group(group)
  group = OptionGroup(parser, "Debug Options")
  group.add_option("--debug", action="store_true", help="Print debug info for the entire app")
  group.add_option("--debug-ssl", action="store_true", help="Print debug info for Ssl class")
  group.add_option("--debug-orion", action="store_true", help="Print debug info for Orion functions")
  parser.add_option_group(group)
  (options, args) = parser.parse_args()
  if options.debug: options.verbose=True
  if options.debug: print ("options " + str(options))
  if options.debug: print ("args " + str(args))
  sys.exit(main())
