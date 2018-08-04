#!/usr/bin/python2
import os, json
from multiprocessing import Pool

import mainExportKicks

def run_stuff(args):
  logFile, outFile = args
  print(logFile)
  print(outFile)
  cache = mainExportKicks.init(logFile)
  mainExportKicks.run(cache, outFile)

if __name__ == "__main__":
  config = json.load(open('../config', 'r'))
  rootDir = "../log"
  work = []

  for root, dirs, files in os.walk(rootDir):
    for file in files:
        if file.endswith(config['log']['name']):
          logFile = os.path.join(root, file)

          outPath = os.path.realpath(os.path.join(root, '../../', config['game']['dirs']['data'], os.path.basename(root)))
          outFile = os.path.join(outPath, ''.join(config['log']['labels']))

          if not os.path.isdir(outPath):
              print "ERROR: data path doesn't exsists (", outPath, ")"
              continue
          
          if os.path.isfile(outFile):
            print "EXISTS ", outFile
            continue

          work.append((logFile, outFile))
             
  if work:
    pool = Pool()
    pool.map(run_stuff, work)

  print("FINISH")