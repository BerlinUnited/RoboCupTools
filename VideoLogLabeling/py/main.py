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
    parser.add_argument('-vf', '--video-file', action='store_true', help="Creates the default video info file, if it doesn't exists.")
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

def load_actions():
    """
    Loads all functions from the Actions file, which doesn't starts with a '_' and returns all found 'action functions'.

    :return:    a dict of action functions
    """
    actions = {}

    for a in dir(Actions):
        # ignore functions beginning with an '_'
        if not a.startswith('_'):
            actions[a] = getattr(Actions, a)

    return actions

def load_gc_actions():
    actions = { 'gtc': {} }

    for a in dir(ActionsGc):
        # ignore functions beginning with an '_'
        if not a.startswith('_'):
            fun = getattr(ActionsGc, a)
            _, defaults = list(filter(lambda m: m[0] == '__defaults__', inspect.getmembers(fun)))[0]
            if defaults:
                for d in defaults:
                    if d not in actions: actions[d] = {}
                    actions[d][a] = fun
            else:
                actions['gtc'][a] = fun

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

def do_work_game(game:Game, args, actions_gc, applying):
    try:
        # check, if video info file should be created or updated
        if args.video_file and not game.has_video_file():
            logging.info("%s / %s - missing video info file! creating default ...", str(game.event), str(game))
            game.create_video_file()
        elif game.has_video_file() and game.has_video_file_changed():
            logging.info("%s / %s - updating video info file ...", str(game.event), str(game))
            game.create_video_file()
        # check if the gamecontroller file needs to be converted
        if game.has_gc_file():
            # convert gamecontroller file first
            if not game.gc.has_converted() and args.gc:
                game.gc.convert(args.gc)
            # retrieve all action names
            actions_gc_keys = set()
            for a in actions_gc.values():
                actions_gc_keys = actions_gc_keys.union(a.keys())
            # check if gamecontroller file needs to be re-created
            if actions_gc_keys - set(game.gc.parsed_actions()) or args.reparse:
                logging.info('%s / %s - missing actions in gamecontroller file! re-creating ...', str(game.event), str(game))
                game.gc.create_info_file(actions_gc)
        return game
    except KeyboardInterrupt:
        # ignore canceled jobs
        pass
    except Exception:
        traceback.print_exc()

def do_work_log(log:Log, dry=False, apply=None, reparse:bool=False, old_sync:bool=False):
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
        # check if the syncing infos with the video exists
        if not log.has_syncing_info() or log.syncing_info_needs_update():
            # print what we do
            if not log.has_syncing_info(): logging.info('%s / %s / %s - missing syncing file! creating default ...', str(log.game.event), str(log.game), str(log))
            else: logging.info('%s / %s / %s - updating syncing file ...', str(log.game.event), str(log.game), str(log))
            # do something, if not 'dry' run
            if not dry:
                log.sync_with_videos()
        # check if old syncing file should be created and currently doesn't exists
        if old_sync and not log.has_syncing_info_old():
            logging.info('%s / %s / %s - missing OLD syncing file! creating default ...', str(log.game.event), str(log.game), str(log))
            if not dry:
                log.sync_with_videos_old()
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
        traceback.print_exc()


if __name__ == "__main__":
    # parse the arguments
    args = parseArguments()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')

    # creates the filter for the events/games if there were some given
    event_filter = None if args.event is None else re.compile('|'.join(['(%s)' % e for e in args.event]))
    game_filter = None if args.game is None else re.compile('|'.join(['(%s)' % e for e in args.game]))

    # init global vars
    events = read_logs(args.path)
    actions = load_actions()
    actions_gc = load_gc_actions()

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

        # do the hard work
        pp = multiprocessing.Pool(1 if args.dry_run else None)
        pp_results = []
        # iterate through events, their games and the log files
        for e in events:
            if event_filter is None or event_filter.match(os.path.basename(e.directory)):
                for g in e.games:
                    if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                        pp_results.append(pp.apply_async(do_work_game, (g, args, actions_gc, actions_applying)))
        # wait for the games to be ready
        while len(pp_results) > 0:
            for r in pp_results:
                if r.ready():
                    # get the result
                    result = r.get()
                    # remove from result list
                    pp_results.remove(r)
                    if isinstance(result, Game):
                        # do work of logs
                        for l in result.logs.values():
                            pp.apply_async(do_work_log, (l, args.dry_run, actions_applying, args.reparse, args.old_sync))


        '''
        if args.dry_run:
            logging.info('Iterate through log files without doing actually something - DRY RUN!')
            # iterate through events, their games and the log files
            for e in events:
                if event_filter is None or event_filter.match(os.path.basename(e.directory)):
                    for g in e.games:
                        if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                            # check, if video info file should be created
                            if args.video_file and not g.has_video_file():
                                logging.info("%s / %s - missing video info file! creating default ...", str(e), str(g))
                            # check work of logs
                            for l in g.logs.values():
                                do_work_log(l, True, actions_applying, args.reparse, args.old_sync)
        else:
            # do the hard work
            pp = multiprocessing.Pool()
            # iterate through events, their games and the log files
            for e in events:
                if event_filter is None or event_filter.match(os.path.basename(e.directory)):
                    for g in e.games:
                        if game_filter is None or game_filter.match(os.path.basename(g.directory)):
                            # check, if video info file should be created or updated
                            if args.video_file and not g.has_video_file():
                                logging.info("%s / %s - missing video info file! creating default ...", str(e), str(g))
                                g.create_video_file()
                            elif g.has_video_file() and g.has_video_file_changed():
                                logging.info("%s / %s - updating video info file ...", str(e), str(g))
                                g.create_video_file()
                            # check if the gamecontroller file needs to be converted
                            if g.has_gc_file():
                                # convert gamecontroller file first
                                if not g.gc.has_converted() and args.gc:
                                    g.gc.convert(args.gc)
                                # retrieve all action names
                                actions_gc_keys = set()
                                for a in actions_gc.values():
                                    actions_gc_keys = actions_gc_keys.union(a.keys())
                                # check if gamecontroller file needs to be re-created
                                if actions_gc_keys - set(g.gc.parsed_actions()) or args.reparse:
                                    logging.info('%s / %s - missing actions in gamecontroller file! re-creating ...', str(g.event), str(g))
                                    g.gc.create_info_file(actions_gc)
                            # do work of logs
                            for l in g.logs.values():
                                pp.apply_async(do_work_log, (l, False, actions_applying, args.reparse, args.old_sync))
        '''
        # wait for workers to finish
        pp.close()
        pp.join()

        logging.info('Done')