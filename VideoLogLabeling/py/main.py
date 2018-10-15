#!/usr/bin/python3
import argparse
import logging
import multiprocessing
import os
import re
import sys
import traceback

sys.path.append(os.path.join(os.path.abspath('.'), 'parsers'))

import Actions
from utils import config, Event


def parseArguments():
    parser = argparse.ArgumentParser(
        description='Iterates through the log files and parses events & actions defined in the Action.py file.',
        epilog= "Example:\n"
                "\t{0}\n"
                "\t\tSearches the default directory and parses missing actions.\n\n"
                "\t{0} -l games\n"
                "\t\tLists all found events and their including games.\n\n"
                "\t{0} -p '/path/to/log/dir' '../../../another/dir'\n"
                "\t\tInstead of the default log directory the given ones are used.\n\n"
                "\t{0} -e '.*RC.*' '2018-04-06_Iran'\n"
                "\t\tFilters all found events with the given pattern.\n\n"
                "\t{0} -d -v -p '/path/to/log/dir' -e '.*RC18.*' '2018-04-06_Iran' -r -f\n"
                "\t\tPerforms a 'dry-run' and uses the given log directory, searches for the event patterns and would fully reparse all found log files.\n\n"
                "".format(os.path.basename(__file__)),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-d', '--dry-run', action='store_true', help="Just iterates over the log files and prints out, what should be done, but doesn't parse anything.")
    parser.add_argument('-l', '--list', action='store', help="Lists some information ('actions', 'events', 'games').")
    parser.add_argument('-r', '--reparse', action='store_true', help='If used with the "--full" or "--action" option, those actions gets reparsed.')
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('-f', '--full', action='store_true', help='If a label file is missing some actions, it gets fully parsed, otherwise only the missing actions are parsed (default).')
    action_group.add_argument('-a', '--action', action='store', nargs='+', help='Specifies the action(s) which should be used while parsing.')
    parser.add_argument('-p', '--path', action='store', nargs='+', default=['../log'], help='Specifies the log directory/directories which should be parsed.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enables debug output.')
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument('-e', '--event', action='store', nargs='+', help='Parse only the given events (regex allowed).')
    filter_group.add_argument('-g', '--game', action='store', nargs='+', help='Parse only the given games (regex allowed).')

    return parser.parse_args()

def read_logs(paths):
    events = []
    if isinstance(paths, str): paths = [paths]
    for p in paths:
        if os.path.isdir(p):
            print('Reading "{}" ...'.format(os.path.abspath(p)))
            # scan for events
            for event in os.listdir(p):
                # make sure, the event directory has the correct naming scheme
                event_dir = os.path.join(p, event)
                event_regex = re.match(config['event']['regex'], event)
                if os.path.isdir(event_dir) and event_regex is not None:
                    events.append(Event(event_dir))
        else:
            print('ERROR: not a valid path: {}'.format(p))

    return events

def load_actions():
    actions = {}

    for a in dir(Actions):
        if not a.startswith('_'):
            actions[a] = getattr(Actions, a)

    return actions

def retrieve_applying_actions(args, actions):
    actions_applying = None
    if args.full:
        actions_applying = list(actions.keys())
    elif args.action:
        actions_applying = [a for a in actions.keys() if a in args.action]
        actions_unavailable = [a for a in args.action if a not in actions.keys()]
        if actions_unavailable:
            print('WARNING: the following action(s) aren\'t available: {}'.format(str(actions_unavailable)))
    return actions_applying

def do_work(log, dry=False, apply=None, reparse=False):
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
        elif set(actions.keys()) - set(log.parsed_actions()) or reparse:
            # retrieve the missing action functions or the ones which should be applied
            missing = {}
            if apply:
                for a in apply: missing[a] = actions[a]
            else:
                for a in set(actions.keys()) - set(log.parsed_actions()): missing[a] = actions[a]
            print("{} / {} / {} - missing actions in label file! re-creating {} ...".format(log.game.event, log.game, log, str(apply)))
            if not dry: log.create_label_file(missing)
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    # parse the arguments
    args = parseArguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # creates the filter for the events/games if there were some given
    event_filter = None if args.event is None else re.compile('|'.join(['(%s)' % e for e in args.event]))
    game_filter = None if args.game is None else re.compile('|'.join(['(%s)' % e for e in args.game]))

    # init global vars
    events = read_logs(args.path)
    actions = load_actions()

    if args.list:
        if args.list == 'actions':
            print('The following actions are used when parsing the log files:')
            for a in actions:
                print("\t{}".format(a))
        elif args.list == 'events':
            print('The following events were found:')
            for e in sorted(events, key=lambda ev: str(ev)):
                print("\t{}".format(e))
        elif args.list == 'games':
            print('The following events and their games were found:')
            for e in sorted(events, key=lambda ev: str(ev)):
                print("\t{}".format(e))
                for g in sorted(e.games, key=lambda ga: str(ga)):
                    print("\t\t{}".format(g))
        else:
            print('ERROR: Unknown list option! Only the following are recognized: actions, events, games')
    else:
        actions_applying = retrieve_applying_actions(args, actions)

        if args.dry_run:
            print('Iterate through log files without doing actually something - DRY RUN!\n')
            # iterate through events, their games and the log files
            for e in events:
                if event_filter is None or event_filter.match(os.path.basename(e.directory)):
                    for g in e.games:
                        if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                            for l in g.logs.values():
                                do_work(l, True, actions_applying, args.reparse)
        else:
            # do the hard work
            pp = multiprocessing.Pool()
            # iterate through events, their games and the log files
            for e in events:
                if event_filter is None or event_filter.match(os.path.basename(e.directory)):
                    for g in e.games:
                        if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                            for l in g.logs.values():
                                pp.apply_async(do_work, (l,False,actions_applying,args.reparse))
            # wait for workers to finish
            pp.close()
            pp.join()

            print('Done')