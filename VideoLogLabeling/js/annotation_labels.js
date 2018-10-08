
const ANNOTATION_LABELS = {
  "basisLabels" : {"title": "Basis", "labels": [
    {"value":"badView",       "name": "<b>view</b> obstructed"},
    {"value":"nokick",        "name": "<b>no kick motion</b> performed"},
    {"value":"delocalized",   "name": "robot <b>delocalized</b>"},
    {"value":"noBall",        "name": "<b>no ball</b> in front of robot"}
  ]},
  "situationLabels" : {"title": "Situation", "labels": [
    {"value":"moved",         "name": "ball <b>moved</b> by the kick"},
    {"value":"touch",         "name": "<b>touch</b> the ball <b>before</b> kick"},
    {"value":"pushed",        "name": "<b>pushed</b> by opponent"},
    {"value":"pushedOwn",     "name": "<b>pushed</b> by teammate"},
    {"value":"fall",          "name": "<b>fall</b> after kick"},
    {"value":"balldirection", "name": "ball moved in the <b>desired direction</b>"},
    {"value":"fallenWithout", "name": "fall <b>without</b> any force"}
  ]},
  "resultLabels" : {"title": "Result", "labels": [
    {"value":"oppgoal",       "name": "<b>goal</b> scored"},
    {"value":"sideOut",       "name": "ball out on a <b>side line</b>"},
    {"value":"ownOut",        "name": "ball out on the <b>own groundline</b>"},
    {"value":"oppOut",        "name": "ball out on the <b>opponent groundline</b>"},
    {"value":"ballToOwnGoal", "name": "ball moved <b>closer to own</b> goal"},
    {"value":"ballToOppGoal", "name": "ball moved <b>closer to opponent</b> goal"}
  ]}
};