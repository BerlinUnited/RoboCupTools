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
  
def hasntall(lst):
  return lambda x: not has(lst)(x)
  
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
  
  
  
  print "game & kicks & out & opp & meh & own \\\\"
  fig = plt.figure()
  
  
  game_id = {
    "2015-04-26-GO-NaoDevils-half2": "old",
    "2015-04-26-GO-NaoDevils-half1": "old",
    "2015-04-26-GO-ZKnipsers-half2": "old",
    "2015-04-26-GO-ZKnipsers-half1": "old",
    "2015-04-25-GO-HULKS-half1": "old",
    
    "2015-07-21-RC-NaoDevils-half2": "new",
    "2015-07-21-RC-NaoDevils-half1": "new",
    "2015-07-21-RC-HTWK-half1":"new",
    "2015-07-21-RC-HTWK-half2":"new",
    "2015-07-20-RC-RoboCanes-half1":"new",
    "2015-07-20-RC-RoboCanes-half2":"new"
    }
  
  stats = {"new":{"kicks":0.0, "md":0.0, "fail":0.0, "succ":0.0, "failedtec":0.0, "pushed":0.0, "loc":0.0, "out":0.0, "opp":0.0, "own":0.0, "meh":0.0}, "old":{"kicks":0.0,"md":0.0 ,"fail":0.0, "succ":0.0, "failedtec":0.0, "pushed":0.0, "loc":0.0, "out":0.0, "opp":0.0, "own":0.0, "meh":0.0}}
  
  index = 0
  # collect stats per game
  for game in j:
    print game
  
    if not game in game_id:
      continue
    
    print game, game_id[game]
    s = stats[game_id[game]]
  
    # flatten the labels
    labels = [parse_labels(event["labels"])
          for log    in j[game]
          for labels in log
          for event  in log[labels]["intervals"]]
    
    # remove the empty ones
    kicks = [l for l in labels if l]
    s["kicks"] += len(kicks)
    
    # motion & direction
    md = filter(has(["moved","balldirection"]), kicks)
    s["md"] += len(md)
    
    # robot was localized => meaningful decision
    localized = filter(hasnt(["delocalized"]), kicks) 
    s["loc"] += numberOf(hasnt(["delocalized"]), kicks)[0]
    
    # technically successful kick
    succ = filter(has(["moved","balldirection"]), localized)
    #succ_test = filter(hasnt(["delocalized"]), md)
    #print "succ ",len(succ), len(succ_test)
    s["succ"] += len(succ)
    
    # fail = not md
    fail = filter(hasntall(["moved","balldirection"]), kicks)
    s["fail"] += len(fail)
    #print "fail ", len(fail) + len(md), len(kicks)
    s["pushed"] += numberOf(has(["pushed"]), fail)[0]
    s["failedtec"] += numberOf(hasnt(["pushed"]), fail)[0]
    #print "test ", numberOf(has(["pushed"]), fail)[0]+ numberOf(hasnt(["pushed"]), fail)[0], len(fail)
    
    
    s["out"] += numberOf(hasone(["oppOut"]), succ)[0]
    #,"ownOut","sideOut"
    
    s["opp"] += numberOf(hasone(["ballToOppGoal","oppgoal"]), succ)[0]
    s["own"] += numberOf(has(["ballToOwnGoal"]), succ)[0]
    s["meh"] += numberOf(hasnt(["ballToOwnGoal","ballToOppGoal","oppgoal"]), succ)[0]
    #print "test ", len(succ), numberOf(has(["ballToOppGoal"]), succ)[0] + numberOf(has(["ballToOwnGoal"]), succ)[0]+numberOf(hasnt(["ballToOwnGoal","ballToOppGoal"]), succ)[0]
    #print numberOf(has(["ballToOppGoal"]), localized)[1], numberOf(has(["ballToOwnGoal"]), localized)[1], numberOf(hasnt(["ballToOwnGoal","ballToOppGoal"]), localized)[1]

    #print numberOf(has(["ballToOppGoal"]), succ)[1], numberOf(has(["ballToOwnGoal"]), succ)[1],numberOf(hasnt(["ballToOwnGoal","ballToOppGoal"]), succ)[1]
    
    #s["fail"] = len(labels) - len(succ)
    
    # pushes
    #s["succ_push"] = len(filter(has(["pushed"]), succ))
    #s["fail_push"] = len(filter(has(["pushed"]), labels)) - len(filter(has(["pushed"]), succ))
    
    
    
    # evaluation
    #s["opp"] = numberOf(has(["ballToOppGoal"]), succ)
    #s["own"] = numberOf(has(["ballToOwnGoal"]), succ)
    #s["meh"] = numberOf(hasnt(["ballToOwnGoal","ballToOppGoal"]), succ)

    #goalScored = numberOf(hasone(["oppgoal"]), succ)
    
    # export for latex
    #print "{:s} & {:d} & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%})  \\\\".format(game, s["succ"], s["out"][0], s["out"][1], s["opp"][0], s["opp"][1],s["meh"][0], s["meh"][1],s["own"][0], s["own"][1])
    
    #plt.bar(np.arange(len(s)) + index*0.35, s.values(), 0.35, color=colors[index], label=game)
    #plt.xticks(np.arange(len(s)), s.keys())
    #index += 1
    
    #numberOfKicks = len(labels)
    
    #ax = fig.add_subplot(3,6,index+1)
    #ax.set_title(game)
    #ax.bar([1,2,3,4,5], [numberOfKicks, s["succ"], len(localized), s["out"][0], goalScored[0]])
    
    #positions = [(parse_labels(event["labels"]), event["ball"])
    #      for log    in j[game]
    #      for labels in log
    #      for event  in log[labels]["intervals"]]
          
    #positions_succ = hasnt(["delocalized"])
    #filter(lambda x: has(["moved","balldirection"])(x[0]), positions)
    
    #ball = [[x[1]["x"], x[1]["y"]] for x in positions if hasnt(["delocalized"])(x[0])]
    #ball_d = zip(*ball)
    #plt.plot(ball_d[0], ball_d[1], 'o', label=game)
    index += 1
  
  
  ax1 = fig.add_subplot(1,3,1)
  ax2 = fig.add_subplot(1,3,2)
  ax3 = fig.add_subplot(1,3,3)
  
  colors = ['r','gray']
  
  index = 0
  for i in stats:
    s = stats[i]
    #plt.bar(np.arange(5) + (index-1)*0.35, np.array([s["kicks"], s["loc"], s["succ"], s["pushed"], s["failedtec"]])/s["kicks"]*100.0, 0.35, color=colors[index], label=i)
    #plt.xticks(np.arange(5), ["kicks","loc","succ", "pushed", "fail tech"])
    
    # main table
    v = np.array([s["md"], s["loc"], s["succ"]])/s["kicks"]
    str = "{:s} & {:d} & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%}) \\\\".format(i, int(s["kicks"]), int(s["md"]), v[0], int(s["loc"]), v[1], int(s["succ"]), v[2])
    print str.replace("%","\\%")
    
    ax1.bar(np.arange(3) + (index-1)*0.35, v*100.0, 0.35, color=colors[index], label=i)
    ax1.set_xticks(np.arange(3))
    ax1.set_xticklabels(["md","loc","succ"])
    
    # evaluation
    u = np.array([s["out"], s["opp"], s["meh"], s["own"]])/s["succ"]
    str = "{:s} & {:d} & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%}) & {:d} ({:.2%}) \\\\".format(i, int(s["succ"]), int(s["out"]), u[0], int(s["opp"]), u[1], int(s["meh"]), u[2], int(s["own"]), u[3])
    print str.replace("%","\\%")
    
    ax2.bar(np.arange(4) + (index-1)*0.35, u*100.0, 0.35, color=colors[index], label=i)
    ax2.set_xticks(np.arange(4))
    ax2.set_xticklabels(["out","opp","meh","own"])
    
    # fails
    v = np.array([s["pushed"], s["failedtec"]])/s["fail"]
    str = "{:s} & {:d} & {:d} ({:.2%}) & {:d} ({:.2%}) \\\\".format(i, int(s["fail"]), int(s["pushed"]), v[0], int(s["failedtec"]), v[1])
    print str.replace("%","\\%")
    
    ax3.bar(np.arange(2) + (index-1)*0.35, v*100.0, 0.35, color=colors[index], label=i)
    ax3.set_xticks(np.arange(2))
    ax3.set_xticklabels(["pushed","failedtec"])
    
    index += 1
    
  plt.legend(loc="best")
  plt.show()
  
  