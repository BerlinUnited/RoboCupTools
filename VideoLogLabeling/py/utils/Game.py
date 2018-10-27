import datetime
import json
import logging
import os
import re
from urllib.parse import urlparse

from .Config import config
from .Log import Log


class Game:
    """Represents a game, its addtional informations and contained logs."""

    def __init__(self, event, dir):
        """Constructor. Initializes class variables and reads some basic information of the game. Also all available
        video files are retrieved and available logs were added."""
        self.event = event
        self.directory = dir

        self.date = None
        self.team_1 = None
        self.team_2 = None
        self.half = 0
        self.logs = {}
        self.videos_file = None
        self.videos = {}

        self.__dirty_v = False
        self.__url_schemes = ['http', 'https']

        self.parse_info()
        self.scan_logs()
        self.scan_videos()

    def parse_info(self):
        """Extracts date, playing teams and halftime based on the configuration regular expression."""
        m = re.match(config['game']['regex'], os.path.basename(self.directory))

        self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d_%H-%M-%S')
        self.team_1 = m.group(2)
        self.team_2 = m.group(3)
        self.half = m.group(4)

    def scan_logs(self):
        """Scans the log directory for matching logs and adds them to the log list."""
        game_logs = os.path.join(self.directory, config['game']['dirs']['nao'])

        if os.path.isdir(game_logs):
            # scan for games at the event
            for log in os.listdir(game_logs):
                # make sure, the game directory has the correct naming scheme
                log_dir = os.path.join(game_logs, log)
                if os.path.isdir(log_dir) and re.match(config['log']['regex'], log):
                    log_data_dir = os.path.join(self.directory, config['game']['dirs']['data'], log)
                    self.logs[log] = Log(self, log_dir, log_data_dir)
                else:
                    logging.getLogger('Game').warning("Invalid log directory!", log_dir)

    def scan_videos(self):
        """First it reads the content of the video info file and then scans the video directory for video files. Only
        configured extensions are used and '.url' files read and the content is added as url source to the video. If the
        video info data is modified, the 'dirty' flag is set."""
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
                            self.__dirty_v = True

                        # skip the remaining extensions
                        break

    def __get_video_file(self):
        """
        Returns the path of the video info file - without any existence checks!

        :return:     path of the vidoe info file
        """
        return os.path.join(self.directory, config['game']['dirs']['data'], config['game']['video_file'])

    def __search_video_file(self, files):
        """
        Searches all videos sources, if the :files: are already part it and returns only those files, which aren't
        part of any video source.

        :param files:   list of files to be checked
        :return:        list of files, which aren't source of a video file
        """
        for n in self.videos:
            # skip already known sources
            for i,file in enumerate(files):
                if file in self.videos[n]['sources']:
                    files[i] = None
        return list(filter(None, files))

    def has_video_file(self):
        """
        Returns True, if a video info file exists, otherwise False

        :return:    True|False
        """
        return self.videos_file is not None

    def has_video_file_changed(self):
        """
        Returns True, if the 'dirty' flag of the video data is set - the video data has changed, otherwise False.

        :return:    True|False
        """
        return self.__dirty_v

    def has_videos(self):
        """
        Returns True, if videos for this game are available, otherwise False.

        :return:    True|False
        """
        return len(self.videos) > 0

    def create_video_file(self):
        """Creates/Writes the video info file."""
        json.dump(self.videos, open(self.__get_video_file(), 'w'), indent=4, separators=(',', ': '))

    def __repr__(self):
        """Returns the string representation of this game."""
        return "{} - {} vs. {} #{} [{}]".format(self.date.strftime('%d.%m.%Y, %H:%M'), self.team_1, self.team_2, self.half, len(self.logs))

