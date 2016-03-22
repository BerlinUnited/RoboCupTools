#!/usr/bin/python

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
  return lambda x: not has(lst)(x)
  
def hasone(lst):
  return lambda x: any((w in x for w in lst))
      
if __name__ == "__main__":
  #path = "http://localhost/VideoLogLabeling/labeledData.php"
  path = "https://www2.informatik.hu-berlin.de/~naoth/videolabeling/labeledData.php"
  
  # get json
  print "urlopen"
  response = urllib2.urlopen(path, timeout=2)
  print "read"
  html = response.read()
  print "load"
  j = json.loads(html)
  
  index = 0
  colors = ['r','y']
  
  # collect stats per game
  for game in j:
    # flatten the labels
    labels = [parse_labels(event["labels"])
          for log    in j[game]
          for labels in log
          for event  in log[labels]["intervals"]]
    
    # remove the empty ones
    labels = [l for l in labels if l]
    
    stats = {"out":0.0, "fail":0.0, "fail_push":0.0, "succ":0.0, "succ_push":0.0, "opp":0.0, "own":0.0, "meh":0.0}
    
    succ = filter(has(["moved","balldirection"]), labels)
    localized = filter(hasnt(["delocalized"]), succ)
    
    stats["succ"] += len(succ)
    stats["fail"] += len(labels) - len(succ)
    
    # pushes
    stats["succ_push"] += len(filter(has(["pushed"]), succ))
    stats["fail_push"] += len(filter(has(["pushed"]), labels)) - len(filter(has(["pushed"]), succ))
    
    # ball out
    stats["out"] += len(filter(hasone(["oppOut","sideOut","ownOut"]), succ))
    stats["out"] = stats["out"] / float(stats["succ"]) * 100.0
    
    # evaluation
    stats["opp"] += len(filter(has(["ballToOppGoal"]), localized)) 
    stats["own"] += len(filter(has(["ballToOwnGoal"]), localized))
    stats["meh"] += (len(localized) - stats["opp"] - stats["own"])
    
    stats["opp"] = stats["opp"] / float(len(localized)) * 100.0
    stats["own"] = stats["own"] / float(len(localized)) * 100.0
    stats["meh"] = stats["meh"] / float(len(localized)) * 100.0
  
    print "score : ", (stats["opp"] - stats["own"])
  
    print game
    print stats
  
    plt.bar(np.arange(len(stats)) + index*0.35, stats.values(), 0.35, color=colors[index], label=game)
    plt.xticks(np.arange(len(stats)), stats.keys())
    index += 1
    
  plt.legend(loc="best")
  plt.show()