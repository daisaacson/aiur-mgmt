#!/usr/bin/env python
__version__ = 0.1

import sys, time
from bs4 import BeautifulSoup
from time import sleep
from urllib2 import urlopen
from itertools import izip_longest
from optparse import OptionParser, OptionGroup

# Motorola SB6120
# TODO: Remove need for hardcoded Power Level fix
# TODO: Remove need to remove line feeds

HOST = "http://192.168.100.1"
URLS = [ "/indexData.htm", "/cmSignalData.htm"]
data = [] # Store all the tables in this table

# Get Data from a Table
def getData(t):
  tmp = []
  table_body = t.find("tbody")
  head = table_body.find_all("th")
  tmp.append([h.text.strip() for h in head])
  rows = table_body.find_all("tr",recursive=False)
  for row in rows:
    cols = row.find_all("td",recursive=False)
    cols = [ele.text.strip() for ele in cols]
    # FIXME: This element is a long string, so shorten it
    if cols and cols[0].startswith("Power Level"):
      cols[0] = "Power Level"
    # Suck everything into one line
    tmp.append([ele.replace('\n',' ') for ele in cols if ele])
  data.append(tmp)

# Print Data to a formated table
def printData(d):
  for table in d:
    columnlengths = listmaxcollen(table)
    #print columnlengths
    for r,row in enumerate(table):
      if r == 2:
        for s in columnlengths:
          print "-"*s, "+",
        print
      if not row:
        continue
      for i, cell in enumerate(row):
        print cell.ljust(columnlengths[i]), "|",
        #print cell,
      print
    print

# Print Data to a log file format
def printLog(d):
  for table in d:
    for r,row in enumerate(table):
      if not row:
        continue
      if r == 0:
        header = row[0]
        continue
      print (time.strftime('%Y-%m-%d %H:%M:%S')),
      print header + "." + row[0] + " = " + ", ".join(row[1:])

# Get column lengths
def listmaxcollen(l):
  tl = []
  for r in l:
    tl.append(map(len,r))
  return [max(a) for a in izip_longest(*tl)]

def main(a):
  try:
    for ui,url in enumerate(URLS):
      # Get page data
      page = BeautifulSoup(urlopen(HOST + url).read())
      # Split each table into its own data set
      for ti,table in enumerate(page.find_all("table")):
        # FIXME: This was a nested table, so force removed it
        if ui == 1 and ti == 1:
          continue
        if options.debug: print table
        getData(table)
  except:
    raise

  if options.log:
    printLog(data)
  else:
    printData(data)

if __name__ == '__main__':
  description = "Modem Status"
  usage = "usage: %prog [options]"
  version = "%prog " + str(__version__)
  if sys.hexversion >= 33949424: # 2.6
    epilog = "Get Motorola Cable Modem Status Data"
    parser = OptionParser(usage=usage, description=description, epilog=epilog, version=version)
  else:
    parser = OptionParser(usage=usage, description=description, version=version)
  group = OptionGroup(parser, "Debug Options")
  group.add_option("-v", "--verbose", action="store_true", help="Print verbose")
  group.add_option("-d", "--debug", action="store_true", help="Print debug")
  parser.add_option_group(group)
  parser.add_option("-l", "--log", action="store_true", help="Print Output")
  (options, args) = parser.parse_args()
  if options.debug: options.verbose=True
  if options.debug: print "options " + str(options)
  if options.debug: print "args " + str(args)
  sys.exit(main(args))
