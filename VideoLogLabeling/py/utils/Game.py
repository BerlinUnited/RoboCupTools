import datetime
import json
import os
import re
from urllib.parse import urlparse

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
        self.videos_file = None
        self.videos = {}

        self.__dirty = 'dirty'
        self.__url_schemes = ['http', 'https']

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
                    log_data_dir = os.path.join(self.directory, config['game']['dirs']['data'], log)
                    self.logs[log] = Log(self, log_dir, log_data_dir)

    def scan_videos(self):
        # read the video info file
        videos_file = self.__get_video_file()
        if os.path.isfile(videos_file):
            self.videos_file = videos_file
            self.videos = json.load(open(videos_file,'r'))

        # scan for the "real" video files
        videos = os.path.join(self.directory, config['game']['dirs']['video'])
        if os.path.isdir(videos):
            for video in os.listdir(videos):
                for ext in config['game']['video_types']:
                    if video.lower().endswith(ext):
                        # files with the same name are recognized as one video
                        name, suffix = os.path.splitext(video)

                        # read content of '.url' files
                        # NOTE: could be more general for 'text' files
                        if ext == 'url':
                            with open(os.path.join(videos, video), 'r') as url_file:
                                video = list(filter(None, [ (l.strip() if urlparse(l.strip()).scheme in self.__url_schemes else None) for l in url_file.readlines() ]))
                        else:
                            # make sure, the var has the same format for url files and normal video files
                            video = [video]

                        # search missing video files
                        video = self.__search_video_file(video)

                        if video:
                            # add new video;
                            if name not in self.videos:
                                self.videos[name] = {
                                    'sources': [],
                                    'events': {
                                        'ready': [ 0.0 ],   # by default it is assumed, that the video starts with the first ready signal
                                        #'finish': [ 0.0 ],  # ... and ends with the finish signal
                                    }
                                }
                            # add all missing video to sources
                            for v in video:
                                self.videos[name]['sources'].append(v)
                            # mark as changed
                            self.videos[self.__dirty] = True

                        # skip the remaining extensions
                        break

    def __get_video_file(self):
        return os.path.join(self.directory, config['game']['dirs']['data'], config['game']['video_file'])

    def __search_video_file(self, files):
        for n in self.videos:
            # skip internal 'dirty' attribute
            if n == self.__dirty: continue
            # skip already known sources
            for i,file in enumerate(files):
                if file in self.videos[n]['sources']:
                    files[i] = None
        return list(filter(None, files))

    def has_video_file(self):
        return self.videos_file is not None

    def has_video_file_changed(self):
        return self.__dirty in self.videos and self.videos[self.__dirty]

    def has_videos(self):
        return len(self.videos) > 0

    def create_video_file(self):
        # remove (internal) dirty attribute
        if self.__dirty in self.videos:
            del self.videos[self.__dirty]
        json.dump(self.videos, open(self.__get_video_file(), 'w'), indent=4, separators=(',', ': '))

    def __repr__(self):
        return "{} - {} vs. {} #{} [{}]".format(self.date.strftime('%d.%m.%Y, %H:%M'), self.team_1, self.team_2, self.half, len(self.logs))

