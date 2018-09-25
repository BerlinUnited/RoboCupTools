import glob
import json
import os
import re
import sys
import datetime
from ConfigParser import ConfigParser

from LogReader import LogReader
import BehaviorParser

config = json.load(open('../config', 'r'))

def find_first_ready_state(file):
    parser = BehaviorParser.BehaviorParser()
    log = BehaviorParser.LogReader(file, parser)

    for frame in log:
        if 'BehaviorStateComplete' in frame.messages:
            m, o = frame["BehaviorStateComplete"]
        else:
            m, o = frame["BehaviorStateSparse"]

        if m['game.state'] == 1:
            return frame.number, frame['FrameInfo'].time

    return None

class Event:
    def __init__(self, dir):
        self.directory = dir

        self.date = None
        self.name = None
        self.games = []

        self.parse_info()
        self.scan_games()

    def parse_info(self):
        m = re.match(config['event']['regex'], os.path.basename(self.directory))
        self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d')

        self.name = m.group(2)

    def scan_games(self):
        # scan for games at the event
        for game in os.listdir(self.directory):
            # make sure, the game directory has the correct naming scheme
            game_dir = os.path.join(self.directory, game)
            if os.path.isdir(game_dir) and re.match(config['game']['regex'], game):
                self.games.append(Game(self, game_dir))

    def __repr__(self):
        return "{} @ {} ({})".format(self.name, self.date.strftime('%d.%m.%Y'), len(self.games))


class Game:
    def __init__(self, event, dir):
        self.event = event
        self.directory = dir

        self.date = None
        self.team_1 = None
        self.team_2 = None
        self.half = 0
        self.logs = {}
        self.videos = []

        self.parse_info()
        self.scan_logs()
        self.scan_videos()

    def parse_info(self):
        m = re.match(config['game']['regex'], os.path.basename(self.directory))

        self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d_%H-%M-%S')
        self.team_1 = m.group(2)
        self.team_2 = m.group(3)
        self.half = m.group(4)

    def scan_logs(self):
        game_logs = os.path.join(self.directory, config['game']['dirs']['nao'])

        if os.path.isdir(game_logs):
            # scan for games at the event
            for log in os.listdir(game_logs):
                # make sure, the game directory has the correct naming scheme
                log_dir = os.path.join(game_logs, log)
                if os.path.isdir(log_dir) and re.match(config['log']['regex'], log):
                    #
                    self.logs[log] = Log(self, log_dir, os.path.join(self.directory, config['game']['dirs']['data'], log))

    def scan_videos(self):
        videos = os.path.join(self.directory, config['game']['dirs']['video'])
        if os.path.isdir(videos):
            for video in os.listdir(videos):
                for ext in config['game']['video_types']:
                    if video.lower().endswith(ext):
                        self.videos.append(video)
                        print(video)

    def __repr__(self):
        return "{} - {} vs. {} #{} [{}]".format(self.date.strftime('%d.%m.%Y, %H:%M'), self.team_1, self.team_2, self.half, len(self.logs))


class Log:
    def __init__(self, game, dir, data_dir):
        self.game = game
        self.directory = dir
        self.data_directory = data_dir

        self.file = None
        self.sync_file = None
        self.labels = []

        self.player_number = 0
        self.nao = None
        self.robot = None

        self.parse_info()
        self.scan_data()

    def parse_info(self):
        log_file = os.path.join(self.directory, config['log']['name'])
        if os.path.isfile(log_file):
            self.file = log_file

        m = re.match(config['log']['regex'], os.path.basename(self.directory))

        self.player_number = m.group(1)
        self.nao = m.group(2)
        self.robot = m.group(3)

    def scan_data(self):
        if os.path.isdir(self.data_directory):
            # set the sync information
            sync_file = os.path.join(self.data_directory, config['log']['sync'])
            if os.path.isfile(sync_file):
                self.sync_file = { 'file': sync_file }
                # TODO: parse this file

            self.labels = glob.glob(self.data_directory+'/'+config['log']['labels'][0]+'*'+config['log']['labels'][1])
            # TODO: parse labels ?

    def has_syncing_file(self):
        return self.sync_file is not None

    def create_default_syncing_file(self):
        print self.directory, self.data_directory, self.file
        if self.file:
            point = find_first_ready_state(self.file)
            if point:
                self.sync_file = os.path.join(self.data_directory, config['log']['sync'])
                with open(self.sync_file, 'w') as sf:
                    sf.writelines([
                        '# generated by extract_sync_points.py\n'
                        'sync-time-video=0.0\n',
                        'sync-time-log='+str(point[1]/1000.0)+'\n',
                        'video-file='+(self.game.videos[0] if self.game.videos else '')+'\n'
                    ])

    def __repr__(self):
        return "Nao{} #{}".format(self.nao, self.player_number)


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

if __name__ == "__main__":
    log_dir = '../log'

    events = read_logs(log_dir)
    print(events)

    for e in events:
        for g in e.games:
            for l in g.logs.values():
                if not l.has_syncing_file():
                    print e, '/', g, '/', l, '- missing syncing file! creating default ...'
                    l.create_default_syncing_file()