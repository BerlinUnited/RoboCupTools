import datetime
import os
import re

from .Config import config
from .Log import Log


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

    def __repr__(self):
        return "{} - {} vs. {} #{} [{}]".format(self.date.strftime('%d.%m.%Y, %H:%M'), self.team_1, self.team_2, self.half, len(self.logs))

