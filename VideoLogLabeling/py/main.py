#!/usr/bin/python3
import os
import re

import Actions
from utils import config, Event


def read_logs(root):
    events = []
    # scan for events
    for event in os.listdir(root):
        # make sure, the event directory has the correct naming scheme
        event_dir = os.path.join(root, event)
        event_regex = re.match(config['event']['regex'], event)
        if os.path.isdir(event_dir) and event_regex is not None:
            events.append(Event(event_dir))

    return events

def load_actions():
    actions = {}

    for a in dir(Actions):
        if not a.startswith('_'):
            actions[a] = getattr(Actions, a)

    return actions

if __name__ == "__main__":
    log_dir = '../log'

    events = read_logs(log_dir)
    print(events)

    actions = load_actions()
    print(actions)

    for e in events:
        for g in e.games:
            for l in g.logs.values():
                # check if the syncing infos with the video exists
                if not l.has_syncing_file():
                    print e, '/', g, '/', l, '- missing syncing file! creating default ...'
                    l.create_default_syncing_file()
                # check if the default label file exits
                if not l.has_label_file():
                    print e, '/', g, '/', l, '- missing label file! creating default ...'
                # check if all actions were parsed
                if [a for a in actions.keys() if a not in l.parsed_actions()]:
                    l.create_label_file(actions)
