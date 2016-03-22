#!/usr/bin/python

import os
import urllib2
import json
import matplotlib.pyplot as plt
import numpy as np

def parse_labels(labels):
  result = []
  for l in labels:
    if isinstance(labels[l], list):
      for ls in labels[l]:
        result.append(ls)
    else:
      result.append(l)
  return result
            
def has(lst):
  return lambda x: all((w in x for w in lst))
  
def hasnt(lst):
  return lambda x: not hasone(lst)(x)
  
def hasone(lst):
  return lambda x: any((w in x for w in lst))
      

def numberOf(f, lst):
  s = filter(f, lst)
  return [len(s), float(len(s))/float(len(lst))]

def readData():
  localPath = './labels_all.json'
  
  if os.path.isfile(localPath):
    with open(localPath, 'r') as f:
      return json.loads(f.read())
  
  #path = "http://localhost/VideoLogLabeling/labeledData.php"
  path = "https://www2.informatik.hu-berlin.de/~naoth/videolabeling/labeledData.php"
  
  # get json
  print "urlopen"
  response = urllib2.urlopen(path, timeout=2)
  print "read"
  html = response.read()
  
  with open(localPath, 'w') as f:
    f.write(html)
  
  print "load"
  return json.loads(html)
      
if __name__ == "__main__":
  
  j = readData()
  
  index = 0
  colors = ['r','y']
  
  print "game & kicks & out & opp & meh & own \\\\"
  
  # collect stats per game
  for game in j:
    # flatten the labels
    labels = [parse_labels(event["labels"])
          for log    in j[game]
          for labels in log
          for event  in log[labels]["intervals"]]
    
    # remove the empty ones
    labels = [l for l in labels if l]
    
    stats = {"out":[0.0,0.0], "fail":[0.0,0.0], "fail_push":[0.0,0.0], "succ":[0.0,0.0], "succ_push":[0.0,0.0], "opp":[0.0,0.0], "own":[0.0,0.0], "meh":[0.0,0.0]}
    
    succ = filter(has(["moved","balldirection"]), labels)
    localized = filter(hasnt(["delocalized"]), succ)
    
    stats["succ"] = len(succ)
    stats["fail"] = len(labels) - len(succ)
    
    # pushes
    #stats["succ_push"] = len(filter(has(["pushed"]), succ))
    #stats["fail_push"] = len(filter(has(["pushed"]), labels)) - len(filter(has(["pushed"]), succ))
    
    # ball out
    stats["out"] = numberOf(hasone(["oppOut","sideOut","ownOut"]), succ)
    
    # evaluation
    stats["opp"] = numberOf(has(["ballToOppGoal"]), localized)
    stats["own"] = numberOf(has(["ballToOwnGoal"]), localized)
    stats["meh"] = numberOf(hasnt(["ballToOwnGoal","ballToOppGoal"]), localized)

    # export for latex
    print "{:s} & {:d} & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%})  \\\\".format(game, stats["succ"], stats["out"][0], stats["out"][1], stats["opp"][0], stats["opp"][1],stats["meh"][0], stats["meh"][1],stats["own"][0], stats["own"][1])
    
    #plt.bar(np.arange(len(stats)) + index*0.35, stats.values(), 0.35, color=colors[index], label=game)
    #plt.xticks(np.arange(len(stats)), stats.keys())
    #index += 1
    
  #plt.legend(loc="best")
  #plt.show()