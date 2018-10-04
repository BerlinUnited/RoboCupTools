#!/usr/bin/python3
import argparse
import multiprocessing
import os
import re

import Actions
from utils import config, Event


def parseArguments():
    parser = argparse.ArgumentParser(
        description='Iterates through the log files and parses events & actions defined in the Action.py file.',
        epilog= "Example:\n"
                "\t{0} \n"
                "".format(os.path.basename(__file__)),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--dry-run', action='store_true', help="Just iterates over the log files and prints out, what should be done, but doesn't parse anything.")
    parser.add_argument('-l','--list', action='store', help="Lists some information ('actions', 'events', 'games').")
    parser.add_argument('--full', action='store_true', help='If a label file is missing some actions, it gets fully parsed, otherwise only the missing actions are parsed (defulat).')

    return parser.parse_args()

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

def do_work(log, dry=False, full=False):
    try:
        # check if the syncing infos with the video exists
        if not log.has_syncing_file():
            print("{} / {} / {} - missing syncing file! creating default ...".format(log.game.event, log.game, log))
            if not dry: log.create_default_syncing_file()
        # check if the default label file exits
        if not log.has_label_file():
            print("{} / {} / {} - missing label file! creating default ...".format(log.game.event, log.game, log))
            if not dry: log.create_label_file(actions)
        # check if all actions were parsed
        elif set(actions.keys()) - set(log.parsed_actions()):
            # retrieve the missing action functions
            missing = {}
            if full:
                missing = actions
            else:
                for a in set(actions.keys()) - set(log.parsed_actions()): missing[a] = actions[a]
            print("{} / {} / {} - missing actions in label file! re-creating {}...".format(log.game.event, log.game, log, 'full' if full else ''))
            if not dry: log.create_label_file(missing)

    except Exception as e:
        print('ERROR: {}'.format(str(e)))


if __name__ == "__main__":
    # parse the arguments
    args = parseArguments()

    # init global vars
    log_dir = '../log'
    events = read_logs(log_dir)
    actions = load_actions()

    if args.list:
        if args.list == 'actions':
            print('The following actions are used when parsing the log files:')
            for a in actions:
                print("\t{}".format(a))
        elif args.list == 'events':
            print('The following events were found:')
            for e in events:
                print("\t{}".format(e))
        elif args.list == 'games':
            print('The following events and their games were found:')
            for e in events:
                print("\t{}".format(e))
                for g in e.games:
                    print("\t\t{}".format(g))
        else:
            print('ERROR: Unknown list option! Only the following are recognized: actions, events, games')
    elif args.dry_run:
        print('Iterate through log files without doing actually something - DRY RUN!\n')
        # iterate through events, their games and the log files
        for e in events:
            for g in e.games:
                for l in g.logs.values():
                    do_work(l, True,args.full)
    else:
        # do the hard work
        pp = multiprocessing.Pool()
        # iterate through events, their games and the log files
        for e in events:
            for g in e.games:
                for l in g.logs.values():
                    pp.apply_async(do_work, (l,False,args.full))
        # wait for workers to finish
        pp.close()
        pp.join()

        print('Done')