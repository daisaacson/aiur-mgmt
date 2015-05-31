#!/usr/bin/env python

import time
from bs4 import BeautifulSoup
from time import sleep
from urllib2 import urlopen
from itertools import izip_longest

HOST = "http://192.168.100.1"
URLS = [ "/indexData.htm", "/cmSignalData.htm"]
data = []

def getData(t):
  tmp = []
  table_body = t.find("tbody")
  head = table_body.find_all("th")
  tmp.append([h.text.strip() for h in head])
  rows = table_body.find_all("tr",recursive=False)
  for row in rows:
    cols = row.find_all("td",recursive=False)
    cols = [ele.text.strip() for ele in cols]
    if cols and cols[0].startswith("Power Level"):
      cols[0] = "Power Level"
    tmp.append([ele.replace('\n',' ') for ele in cols if ele])
  data.append(tmp)

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

def listmaxcollen(l):
  tl = []
  for r in l:
    tl.append(map(len,r))
  return [max(a) for a in izip_longest(*tl)]

try:
  for ui,url in enumerate(URLS):
    page = BeautifulSoup(urlopen(HOST + url).read())
    for ti,table in enumerate(page.find_all("table")):
      if ui == 1 and ti == 1:
        continue
      #print "===", ui, ti
      #print table
      getData(table)
except:
  raise

#printData(data)
printLog(data)
