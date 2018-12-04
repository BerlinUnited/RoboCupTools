#!/usr/bin/python3
import argparse
import inspect
import logging
import multiprocessing
import os
import re
import subprocess
import sys
import traceback

sys.path.append(os.path.join(os.path.abspath('.'), 'parsers'))

import Actions
import ActionsGc
from utils import config, Event, Log, Game


def parseArguments():
    """
    Parses the application arguments and returns the values as Namespace.
    Errors during parsing and showing the help message is also handled here.

    :return: the Namespace with the parsed arguments
    """
    gc_converter = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../GcTeamcommConverter/dist/GcTeamcommConverter.jar'))
    parser = argparse.ArgumentParser(
        description='Iterates through the log files and parses events & actions defined in the Action.py file.',
        epilog= "Example:\n"
                "\t\033[1m{0}\033[0m\n"
                "\t\tSearches the default directory and parses missing actions.\n\n"
                "\t\033[1m{0} -l games\033[0m\n"
                "\t\tLists all found events and their including games.\n\n"
                "\t\033[1m{0} -p '/path/to/log/dir' '../../../another/dir'\033[0m\n"
                "\t\tInstead of the default log directory the given ones are used.\n\n"
                "\t\033[1m{0} -e '.*RC.*' '2018-04-06_Iran'\033[0m\n"
                "\t\tFilters all found events with the given pattern.\n\n"
                "\t\033[1m{0} -d -v -p '/path/to/log/dir' -e '.*RC18.*' '2018-04-06_Iran' -r -f\033[0m\n"
                "\t\tPerforms a 'dry-run' and uses the given log directory, searches for the event patterns and would fully reparse all found log files.\n\n"
                "".format(os.path.basename(__file__)),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-d', '--dry-run', action='store_true', help="Just iterates over the log files and prints out, what should be done, but doesn't parse anything.")
    parser.add_argument('-l', '--list', action='store', help="Lists some information ('actions', 'events', 'games', 'videos').")
    parser.add_argument('-r', '--reparse', action='store_true', help='If used with the "--full" or "--action" option, those actions gets reparsed.')
    parser.add_argument('--old-sync', action='store_true', help='Enables creating the old sync file format.')
    parser.add_argument('--gc', default=gc_converter, action='store', help='Sets the converter for the gamecontroller log files. By default the converter of the naoth rc toolbox is used.')
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
    """
    Iterates over the given log paths and tries to find events (directories) with the correct name pattern.

    :param paths:   a list of or just a single path to events
    :return:        returns a list of the found events
    """
    events = []
    # we expect a list of paths, make it one if its just a string
    if isinstance(paths, str): paths = [paths]
    # iterate over the given paths
    for p in paths:
        if os.path.isdir(p):
            logging.info('Reading %s', os.path.abspath(p))
            # scan for events
            for event in os.listdir(p):
                # make sure, the event directory has the correct naming scheme
                event_dir = os.path.join(p, event)
                # skip files
                if not os.path.isdir(event_dir): continue
                # check directory name
                event_regex = re.match(config['event']['regex'], event)
                if event_regex is not None:
                    events.append(Event(event_dir))
                else:
                    logging.warning('Not a valid event directory: %s', event_dir)
        else:
            logging.warning('Not a directory: %s', p)

    return events

def load_actions(mod):
    """
    Loads all functions from the Actions file, which doesn't starts with a '_' and returns all found 'action functions'.

    :return:    a dict of action functions
    """
    actions = {}

    for a in dir(mod):
        # ignore functions beginning with an '_'
        if not a.startswith('_'):
            actions[a] = getattr(mod, a)

    return actions

def retrieve_applying_actions(args, actions):
    """
    Filters the given :actions: functions based on the application arguments.

    :param args:    parsed application arguments
    :param actions: the actions which should be filtered
    :return:        the filtered action functions
    """
    actions_applying = None
    if args.full:
        actions_applying = list(actions.keys())
    elif args.action:
        actions_applying = [a for a in actions.keys() if a in args.action]
        actions_unavailable = [a for a in args.action if a not in actions.keys()]
        if actions_unavailable:
            logging.warning('The following action(s) aren\'t available: %s', str(actions_unavailable))
    return actions_applying

def check_gc_converter(converter:str):
    """
    Checks, whether the given :converter: is a valid file and can be executed as java application.

    :param converter:   the converter to test
    :return:            True|False
    """
    # check existence
    if not os.path.isfile(converter):
        return False
    # try to execute
    result = subprocess.run(['java', '-jar', converter, '-h'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        # execution failed!
        return False
    return True

def filter_games(events, event_filter, game_filter):
    games = []
    # iterate through events, their games and the log files
    for e in events:
        if event_filter is None or event_filter.match(os.path.basename(e.directory)):
            for g in e.games:
                if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                    games.append(g)
    return games

def do_game_video(game:Game):
    try:
        # check, if video info file should be created or updated
        if not game.has_video_file():
            logging.info("%s / %s - missing video info file! creating default ...", str(game.event), str(game))
            if not args.dry_run: game.create_video_file()
        elif game.has_video_file() and game.has_video_file_changed():
            logging.info("%s / %s - updating video info file ...", str(game.event), str(game))
            if not args.dry_run: game.create_video_file()
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        logging.error("An error occurred updating video file of %s", game)
        traceback.print_exc()
    return game

def do_game_gc(game:Game, reparse:bool, actions_gc:dict, converter:str=None):
    try:
        # check if the gamecontroller file needs to be converted
        if game.has_gc_file():
            # convert gamecontroller file first
            if not game.gc.has_converted() and converter:
                if not args.dry_run: game.gc.convert(converter)
            # check if gamecontroller file needs to be re-created
            if reparse or set(actions_gc.keys()) - set(game.gc.parsed_actions()):
                logging.info('%s / %s - missing actions in gamecontroller file! re-creating ...', str(game.event), str(game))
                if not args.dry_run: game.gc.create_info_file(actions_gc)
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        logging.error("An error occurred during conversion of gamecontroller of %s", game)
        traceback.print_exc()
    return game

def do_log(log:Log, dry=False, apply=None, reparse:bool=False):
    """
    Does the actual work. It creates the info file, the syncing info if they doesn't exists and applies the action functions
    if requested or if necessary.

    :param log: the log file to work on
    :param dry: True, if run without modifications, False otherwise (default)
    :param apply:   which action functions should be applied
    :param reparse: True, if the logs be reparsed with the applying action functions, otherwise False (default)
    :return:    None
    """
    try:
        logging.debug('%s / %s / %s - processing log ...', str(log.game.event), str(log.game), str(log))
        # check if the default label file exits
        if not log.has_info_file():
            logging.info('%s / %s / %s - missing info file! creating default ...', str(log.game.event), str(log.game), str(log))
            if not dry: log.create_info_file(actions)
        # check if all actions were parsed
        elif set(actions.keys()) - set(log.parsed_actions()) or reparse:
            # retrieve the missing action functions or the ones which should be applied
            missing = {}
            if apply:
                for a in apply: missing[a] = actions[a]
            else:
                for a in set(actions.keys()) - set(log.parsed_actions()): missing[a] = actions[a]
            logging.info('%s / %s / %s - missing actions in label file! re-creating %s ...', str(log.game.event), str(log.game), str(log), str(apply))
            if not dry: log.create_info_file(missing)
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        logging.error("An error occurred during processing log %s", log)
        traceback.print_exc()

def do_sync(game:Game):
    """
    Tries to synchronize the log files of the game.

    :param game:
    :return: return a synchronized game
    """
    try:
        if not all([ l.has_syncing_info() for l in game.logs.values() ]):
            if not args.dry_run: game.sync()
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        logging.error("An error occurred during synchronization of %s", game)
        traceback.print_exc()

    return game

if __name__ == "__main__":
    # parse the arguments
    args = parseArguments()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')

    # creates the filter for the events/games if there were some given
    event_filter = None if args.event is None else re.compile('|'.join(['(%s)' % e for e in args.event]))
    game_filter = None if args.game is None else re.compile('|'.join(['(%s)' % e for e in args.game]))

    # init global vars
    events = read_logs(args.path)
    actions = load_actions(Actions)
    actions_gc = load_actions(ActionsGc)

    # checks the gc converter and 'disables' conversion, if the converter doesn't exist
    if not check_gc_converter(args.gc):
        logging.info("Invalid GameController converter! GC files aren't converted.")
        args.gc = None

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
        elif args.list == 'videos':
            print('The following events and their game videos were found:')
            for e in sorted(events, key=lambda ev: str(ev)):
                print("\t{}".format(e))
                for g in sorted(e.games, key=lambda ga: str(ga)):
                    if g.has_videos():
                        print("\t\t{}".format(g))
                        for v in g.videos:
                            print("\t\t\t{}: {}".format(v, ', '.join(g.videos[v]['sources'])))
        else:
            logging.error('Unknown list option! Only the following are recognized: actions, events, games')
    else:
        actions_applying = retrieve_applying_actions(args, actions)
        games = filter_games(events, event_filter, game_filter)

        if games:
            # do the hard work
            pp = multiprocessing.Pool(1 if args.dry_run else None)

            logging.info("Create/Update video files ...")
            # doesn't change the objects:
            pp.map(do_game_video, games)

            logging.info("Create/Update gamecontroller info files ...")
            # the GC log is (evtl.) changed ...
            pp.starmap(do_game_gc, [(g, args.reparse, actions_gc, args.gc) for g in games])
            # reload log data
            for g in games:
                if g.gc: g.gc.reload()

            logging.info("Create/Update log info files ...")
            # the log is (evtl.) changed ...
            pp.starmap(do_log, [ (l, args.dry_run, actions_applying, args.reparse) for g in games for l in g.logs.values() ])
            # reload log data
            for l in [ l for g in games for l in g.logs.values() ]:
                l.reload()

            logging.info("Synchronize game log files ...")
            pp.map(do_sync, games)

        else:
            logging.info("No games found or filter doesn't match any event/game.")

        logging.info('Done')