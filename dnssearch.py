#!/usr/bin/env /usr/bin/python
__version__ = 0.1
import sys, re, time, os, subprocess, itertools
from optparse import OptionParser, OptionGroup

DUMPFILE = ""
TIMEOUT = 30
dnsrecords = []
results = []
rrtypes = ['a','aaaa','cname','dname','mx','ptr']
norecurse = ['mx', 'ns', 'soa']

# 1 list of 8 dns records, each dns record contains a list of record items
## [['owner-name', 'ttl', 'class', 'a',     'ipv4'                                                           ],
##  ['name',       'ttl', 'class', 'aaaa',  'ipv6'                                                           ], 
##  ['name',       'ttl', 'class', 'cname', 'cononical name'                                                 ],
##  ['owner-name', 'ttl', 'class', 'dname', 'redirection-name'                                               ],
##  ['owner-name', 'ttl', 'class', 'mx',    'pref',            'name'                                        ],
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

# Search for DNS records that matched our search results
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
        if options.recursive and dnsrecord[3] not in norecurse:
          # For the found dns record, use the first and last record item to recusivley search for more results
          dnssearch(dnsrecord[0])
          dnssearch(dnsrecord[-1])
        # If dns record is an a record, search for ptr in the event the forward and reverse names doesn't match
        if dnsrecord[3] == 'a':
          arpa = get_arpa_address(dnsrecord[-1])
          if options.verbose: print "need to find ptr", arpa
          dnssearch(arpa)

# Turn and IP address to and in-addr.arpa address
def get_arpa_address(ip):
  if options.verbose: print ip, "to arpa:", '.'.join(ip.split('.')[::-1]) + '.in-addr.arpa.'
  return '.'.join(ip.split('.')[::-1]) + '.in-addr.arpa.'

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

  # These next two steps have to be independent, other wise a race condition occurs
  ## We read the end of line of old dump file and it reads "; Dump complete"
  ## named then starts writing to the dump file, not completing the dump, causing the conditon to pass
  ## Therefore, these two test need to be independent
  # Wait for DUMPFILE to be modified
  while not mtime(DUMPFILE) > ftime:
    time.sleep(0.001)
    # Timeout if we are waiting too long
    if time.time() - stime >= TIMEOUT:
      raise ValueError("Timeout", TIMEOUT, DUMPFILE)
  # Wait for DUMPFILE to complete
  while not o == "; Dump complete":
    try:
      p = subprocess.Popen(["tail", "-n", "1", DUMPFILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      o = p.communicate()[0].strip()
    except:
      pass
    time.sleep(0.001)
    # Timeout if we are waiting too long
    if time.time() - stime >= TIMEOUT:
      raise ValueError("Timeout", TIMEOUT, DUMPFILE)

# Get the longest length for each column
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

# Get Records from file
def getrecords():
  try:
    fexist= mtime(DUMPFILE)
    if options.dumpdb:
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
    # Clean up file if it didn't exist prior to running
    if fexist == 0:
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
  return dnsrecords

def main(a):
  global dnsrecords
  global DUMPFILE
  SEARCH = a[0]
  DUMPFILE = a[1]

  dnsrecords = getrecords()

  # Create regex object
  regex = re.compile(SEARCH, re.I)

  if options.zone:
    regex = re.compile(SEARCH+'\.$', re.I)
    for dnsrecord in dnsrecords:
      if regex.search(dnsrecord[0]): results.append(dnsrecord)
  else: 
    # Search first and last record item of all the dns records using regular expression
    ## Save record item to list of recorditmes
    recorditems =  [line[0]  for line in dnsrecords if len(line) > 4 and line[3] in rrtypes and regex.search(line[0])]
    recorditems += [line[-1] for line in dnsrecords if len(line) > 4 and line[3] in rrtypes and regex.search(line[-1])]
    # If the SEARCH items is an IP, look for in-addr.arpa record
    regex_ip = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    if regex_ip.match(SEARCH):
      recorditems += [get_arpa_address(SEARCH)]

    # For each record item, start a search for dns records
    if options.verbose: print set(recorditems)
    for recorditem in set(recorditems):
      if options.verbose: print "looking for: ", recorditem
      try:
        dnssearch(recorditem)
      except RuntimeEror as e:
        results.append(["Error: Too many results:", e[0]])
      except:
        results.append(["Error:", sys.exc_info()[1]])

  # Print our findings
  if options.verbose: print results
  print "Results on", os.uname()[1], "for:", SEARCH
  if results:
    if options.sort: printresults(sorted(results, key=lambda x: x[0].split('.')[::-1]))
    else: printresults(results)
  else:
    print "0: Search for " + SEARCH + " found 0 results"

if __name__ == '__main__':
  description = "DNS Searcher"
  usage = "usage: %prog [options] search file"
  version = "%prog " + str(__version__)
  parser = OptionParser(usage=usage, description=description, version=version)
  epilog = "Recursively serch for dns recores on a dns server"
  parser = OptionParser(usage=usage, description=description, epilog=epilog, version=version)
  parser.set_defaults(dumpdb=True)
  parser.set_defaults(recursive=True)
  parser.add_option("-d", "--dumpdb", action="store_true", help="Run rndc --dumpdb to get latest file")
  parser.add_option("-n", "--no-dumpdb", action="store_false", dest="dumpdb", help="Run rndc --dumpdb to get latest file")
  parser.add_option("-r", "--recursive", action="store_true", help="For each result, search for additional matches")
  parser.add_option("-R", "--nonrecursive", action="store_false", dest="recursive", help="Do not recursivly search for mor matches")
  parser.add_option("-s", "--sort", action="store_true", help="Sort output by FQDN")
  parser.add_option("-z", "--zone", action="store_true", default=False, help="Print zone content")
  group = OptionGroup(parser, "Debug Options")
  group.add_option("-v", "--verbose", action="store_true", help="Print Verbose") 
  group.add_option("-D", "--debug", action="store_true", help="Print debug")
  parser.add_option_group(group)
  (options, args) = parser.parse_args()
  if options.zone and options.sort: parser.error("options sorting of zone files is not supported yet.")
  if options.debug: options.verbose=True
  if options.debug: print "options " + str(options)
  if options.debug: print "args " + str(args)
  if len(args) != 2:
    print usage
    sys.exit(2)
  sys.exit(main(args))
