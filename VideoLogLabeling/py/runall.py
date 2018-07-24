#!/usr/bin/python
import os, sys, getopt
from multiprocessing import Process
import mainExportKicks

def run_stuff(logFile, outFile):
  print(logFile)
  print(outFile)
  cache = mainExportKicks.init(logFile)
  mainExportKicks.run(cache, outFile)

if __name__ == "__main__":

  rootDir = "../log"
  
  max_number_of_processes = 4
  threads = []
  
  for root, dirs, files in os.walk(rootDir):
    for file in files:
        if file.endswith(".log"):
          logFile = os.path.join(root, file)
          outFile = os.path.join(root, "labels.json")
          
          if os.path.isfile(outFile):
            print "EXISTS ", outFile
            continue
          
          try:
             p = Process(target=run_stuff, args=(logFile, outFile, ))
             threads.append(p)
             p.start()
          except:
             print "Error: unable to start thread"
             
             
  for t in threads:
    t.join()