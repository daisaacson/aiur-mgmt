#!/usr/bin/env /usr/bin/python
__version__ = 0.1
import sys, re, time, os, subprocess, itertools
from optparse import OptionParser, OptionGroup

DUMPFILE = ""
TIMEOUT = 30
dnsrecords = []
results = []
rrtypes = ['a','aaaa','cname','dname','mx','ptr']

# 1 list of 8 dns records, each dns record contains a list of record items
## [['owner-name', 'ttl', 'class', 'a',     'ipv4'                                                           ],
##  ['name',       'ttl', 'class', 'aaaa',  'ipv6'                                                           ], 
##  ['name',       'ttl', 'class', 'cname', 'cononical name'                                                 ],
##  ['owner-name', 'ttl', 'class', 'dname', 'redirection-name'                                               ],
##  ['owner-name', 'ttl', 'class', 'mx',    'pref', 'name'                                                   ],
##  ['owner-name', 'ttl', 'class', 'ns',    'target-name'                                                    ],
##  ['name',       'ttl', 'class', 'ptr',   'name'                                                           ],
##  ['owner-name', 'ttl', 'class', 'soa',   'name-server',     'email-addr', 'sn', 'ref', 'ret', 'ex', 'min' ]]

# Locations of interest by index
## a     0, 4, -1
## aaaa  0, 4, -1
## cname 0, 4, -1
## dname 0, 4, -1
## mx    0, 5, -1
## ns    0, 4, -1
## ptr   0, 4, -1
## soa   0, 4, -7

def dnssearch (search):
  if options.debug: print "in dnssearch()"
  if options.verbose: print "searching for:", search
  if options.debug: print "dnsrecords:",dnsrecords
  # For each dns record
  for dnsrecord in dnsrecords:
    if options.debug: print "dnsrecord:", dnsrecord
    # See if our search equals a record item, and the record itmes is of a certain type
    if search in dnsrecord and dnsrecord[3] in rrtypes:
      if options.verbose: print "found: ", dnsrecord
      # If we have a match that we haven't found before
      if not dnsrecord in results:
        if options.verbose: print "adding: ", dnsrecord 
        # Add dns record to our results list
        results.append(dnsrecord)
        # Remove dns record from your dns records lists, so recursive matches don't have to reiterate over already found dns records
        dnsrecords.remove(dnsrecord)
        # For the found dns record, use the first and last record item to recusivley search for more results
        dnssearch(dnsrecord[0])
        dnssearch(dnsrecord[-1])
        # If dns record is an a record, search for ptr in the event the forward and reverse names doesn't match
        if dnsrecord[3] == 'a':
          arpa = '.'.join(dnsrecord[-1].split('.')[::-1]) + '.in-addr.arpa.'
          if options.verbose: print "need to find ptr", arpa
          dnssearch(arpa)

# Get modify time of file, if not exist, return 0
def mtime(f):
  try:
    return os.stat(f).st_mtime
  except:
    return 0

# Run rndc and wait for dumpfile to be output
def rndc():
  o = ""
  # Last modification of DUMPFILE
  ftime = mtime(DUMPFILE)
  # Tell named to create a dump file of zones
  try:
    subprocess.Popen(['rndc', 'dumpdb', '-zones'])
  except:
    raise
  # Start time
  stime = time.time()
  # Wait for DUMPFILE to be modified and dump to complete
  while ftime >= mtime(DUMPFILE) or not o == "; Dump complete":
    try:
      p = subprocess.Popen(["tail", "-n", "1", DUMPFILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      o = p.communicate()[0].strip()
    except:
      pass
    time.sleep(0.001)
    # Timeout if we are wating too long
    if time.time() - stime >= TIMEOUT:
      raise ValueError("Timeout", TIMEOUT, DUMPFILE)

# Get the longest lenght for each column
def listmaxcollen(l):
  tl = []
  for r in l:
    tl.append(map(len, r))
  return [max(a) for a in itertools.izip_longest(*tl)]

# Print results in a grid form
def printresults(rs):
  columnlengths=listmaxcollen(rs)
  # Adjust columnlengths with mx records
  if len(columnlengths) == 6:
    columnlengths[4] = 2
  if options.debug: print rs, columnlengths
  for i, result in enumerate(rs):
    # Print line numbers
    print str(i+1).rjust(len(str(len(rs))))+":",
    # Adjust columnlengths with mx records
    if len(columnlengths) == 6 and result[3] != 'mx':
      result.insert(4, '')
    # Print each column entry
    for j, r in enumerate(result):
      print r.ljust(columnlengths[j]),
    print

def main(a):
  global dnsrecords
  global DUMPFILE
  SEARCH = a[0]
  DUMPFILE = a[1]

  try:
    rndc()
    # Open the DUMPFILE readonly
    with open(DUMPFILE, 'r') as dumpfile:
      # Read all dnsrecords that don't begin with ';'
      ## Set line to lower. Makes for easier recursive serches
      ## Strips white space from beginning and end of line
      ## Split words into list. 
      ### dnsrecords is a list of recod lists
      dnsrecords = [line.lower().strip().split() for line in dumpfile if not line.startswith(';')]
      if options.debug: print dnsrecords
    dumpfile.close()
    os.remove(DUMPFILE)
  except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    raise
  except ValueError as e:
    print e[0], "after waiting", e[1], "seconds for", e[2]
    raise
  except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

  # Create regex object
  regex = re.compile(SEARCH, re.I)

  # Search first and last record item of all the dns records using regular expression
  ## Save record item to list of recorditmes
  recorditems =  [line[0] for line in dnsrecords if len(line) > 4 and line[3] in rrtypes and regex.search(line[0])]
  recorditems += [line[-1] for line in dnsrecords if len(line) > 4 and line[3] in rrtypes and regex.search(line[-1])]

  # For each record item, start a search for dns records
  if options.verbose: print set(recorditems)
  for recorditem in set(recorditems):
    if options.verbose: print "looking for: ", recorditem
    dnssearch(recorditem)

  # Print our findings
  print "Results on", os.uname()[1], "for:", SEARCH
  printresults(results)

if __name__ == '__main__':
  description = "DNS Searcher"
  usage = "usage: %prog [options] search file"
  version = "%prog " + str(__version__)
  parser = OptionParser(usage=usage, description=description, version=version)
  if sys.hexversion >= 33949424: # 2.6
    epilog = "Recursively serch for dns recores on a dns server"
    parser = OptionParser(usage=usage, description=description, epilog=epilog, version=version)
  else:
    parser = OptionParser(usage=usage, description=description, version=version)
  group = OptionGroup(parser, "Debug Options")
  group.add_option("-v", "--verbose", action="store_true", help="Print Verbose") 
  group.add_option("-d", "--debug", action="store_true", help="Print debug")
  parser.add_option_group(group)
  (options, args) = parser.parse_args()
  if options.debug: options.verbose=True
  if options.debug: print "options " + str(options)
  if options.debug: print "args " + str(args)
  if len(args) != 2:
    print usage
    sys.exit(2)
  sys.exit(main(args))
