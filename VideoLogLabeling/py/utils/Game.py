import datetime
import json
import logging
import os
import re
import sys
from urllib.parse import urlparse
from typing import Dict, Any

from parsers import LogReaderV2, TeamMessage_pb2

from .GcLog import GcLog
from .Config import config
from .Log import Log


class Game:
    """Represents a game, its addtional informations and contained logs."""

    def __init__(self, event, dir):
        """Constructor. Initializes class variables and reads some basic information of the game. Also all available
        video files are retrieved and available logs were added."""
        self.event = event
        self.directory = dir

        self.date = None    # type: datetime
        self.team_1 = None  # type: str
        self.team_2 = None  # type: str
        self.half = 0
        self.logs = {}      # type: Dict[str, Log]
        self.videos_file = None  # type: str
        self.videos = {}    # type: Dict[Any, Any]
        self.gc = None      # type: GcLog

        self.__dirty_v = False
        self.__url_schemes = ['http', 'https']

        self.parse_info()
        self.scan_logs()
        self.scan_videos()
        self.scan_gc_logs()

    def __log(self):
        return logging.getLogger(__class__.__name__)

    def parse_info(self):
        """Extracts date, playing teams and halftime based on the configuration regular expression."""
        m = re.match(config['game']['regex'], os.path.basename(self.directory))
        if m:
            self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d_%H-%M-%S')
            self.team_1 = m.group(2)
            self.team_2 = m.group(3)
            self.half = m.group(4)
        else:
            self.__log().debug("Game directory doesn't match regex: %s", self.directory)

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
                    self.__log().warning("Invalid log directory: %s", log_dir)
        else:
            self.__log().debug("Game has no log directories!")

    def scan_videos(self):
        """First it reads the content of the video info file and then scans the video directory for video files. Only
        configured extensions are used and '.url' files read and the content is added as url source to the video. If the
        video info data is modified, the 'dirty' flag is set."""
        # read the video info file
        videos_file = self.__get_video_file()
        if os.path.isfile(videos_file):
            self.__log().debug("Read game's video info file: %s", videos_file)
            self.videos_file = videos_file
            self.videos = json.load(open(videos_file,'r'))
        else:
            self.__log().debug("Game has no video info file: %s", videos_file)

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
                            self.__log().debug("Read url video file: %s", video)
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
                                self.__log().debug("Adding video to game: %s", name)
                                self.videos[name] = {
                                    'sources': [],
                                    'events': {
                                        'ready': [ 0.0 ],   # by default it is assumed, that the video starts with the first ready signal
                                        #'finish': [ 0.0 ],  # ... and ends with the finish signal
                                    },
                                    'sync': 0.0
                                }
                            # add all missing video to sources
                            for v in video:
                                self.__log().debug("Adding source to video: %s -> %s", name, v)
                                self.videos[name]['sources'].append(v)
                            # mark as changed
                            self.__dirty_v = True

                        # skip the remaining extensions
                        break
        else:
            self.__log().debug("Game has video directory: %s", str(self))

    def scan_gc_logs(self):
        """Scans the log directory for matching gamecontroller logs."""
        gc_logs = os.path.join(self.directory, config['game']['dirs']['gc'])
        if os.path.isdir(gc_logs):
            # scan for matching file
            for log in os.listdir(gc_logs):
                gc_log_file = os.path.join(gc_logs, log)
                # does it match
                if os.path.isfile(gc_log_file) and re.fullmatch(config['gc']['regex'], log):
                    # already have a gamecontroller log file?
                    if self.gc is None:
                        log_data_dir = os.path.join(self.directory, config['game']['dirs']['data'])
                        self.gc = GcLog(gc_log_file, log_data_dir)
                    else:
                        self.__log().warning("Found multiple gamecontroller log files, the should only be one! (ignoring the others)")
            # some debug output
            if not self.gc:
                self.__log().debug("No gamecontroller log file found.")
        else:
            self.__log().debug("Game has no gamecontroller log directory!")

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

    def __create_data_directory(self):
        """Creates the data directory if necessary."""
        directory = os.path.join(self.directory, config['game']['dirs']['data'])
        if not os.path.isdir(directory):
            self.__log().debug("Create data directory: %s", directory)
            os.mkdir(directory)

    def create_video_file(self):
        """Creates/Writes the video info file."""
        self.__create_data_directory()
        self.__log().debug("Create video info file: %s", self.__get_video_file())
        json.dump(self.videos, open(self.__get_video_file(), 'w'), indent=4, separators=(',', ': '))

    def has_gc_file(self):
        """
        Returns True, if a gamecontroller log file exits, otherwise False.

        :return:    True|False
        """
        return self.gc is not None

    def sync(self):
        self.__log().info("Read log files of %s", str(self))
        # initializes log readers for each log file
        players = {}
        for l in self.logs:
            players[int(self.logs[l].player_number)] = {
                'key': l,
                'reader': LogReaderV2.LogReader(self.logs[l].file),
                'synced': False
            }

        # is gamecontroller data available - sync with gamecontroller
        if self.has_gc_file() and self.gc.has_converted():
            self.__sync_with_gamecontroller(players)

        # is there's still un-synchronized logs, sync with teamcomm
        if not all(map(lambda p: p['synced'], players.values())):
            self.__sync_with_teamcomm(players)

        # post-processing
        for p in players.values():
            # close log readers
            p['reader'].close()
            # report non-synced logs
            if not p['synced']:
                self.__log().warning("Couldn't find syncing point for %s", self.logs[p['key']])

    def __sync_with_gamecontroller(self, players):
        self.__log().info("syncing data with gamecontroller log file: %s", str(self))

        # the gamecontrollers first ready state is used as synchronization point
        point = -1
        for msg in self.gc.data():
            if 'packetNumber' in msg and 'gameState' in msg and msg['gameState'] == 1:
                point = msg['timestamp']
                break

        # if ready state not found, just use the first frame as syncing point
        if point == -1:
            point = self.gc.data()[0]['timestamp']

        # save the found syncing points
        self.gc.set_sync_point(point)

        # iterate through gamecontroller messages
        for msg in self.gc.data():
            # only examine teammessages of players which aren't synced yet
            if 'playerNum' in msg and msg['playerNum'] in players and not players[msg['playerNum']]['synced']:
                # convert custom message part json data to bytes
                msg_data = bytes(map(lambda i: i % 256, msg['data']))#bytes(list(map(lambda i: -128 * (i // 128) + (i % 128), msg['data'])))
                # try to find the binary data in the log file (from the beginning)
                # NOTE: skipping the MixedTeam part, 'cause we don't have it in the log!
                offset = players[msg['playerNum']]['reader'].mm.find(msg_data[12:], 0)
                # found the message in the log?
                if offset != -1:
                    self.__log().debug("found message of %d in gamecontroller log, determine containing frame ...", msg['playerNum'])
                    # find the frame containing the offset
                    for f in players[msg['playerNum']]['reader'].frames:
                        if f.offset['start'] <= offset and offset <= f.offset['end']:
                            self.logs[players[msg['playerNum']]['key']].set_sync_point((f['FrameInfo'].time - (msg['timestamp'] - point))/1000.0)
                            players[msg['playerNum']]['synced'] = True
                            break
            # found syncing infos for all log, can stop loop
            if all(map(lambda p: p['synced'], players.values())): break

    def __sync_with_teamcomm(self, players):
        self.__log().info("syncing data with teamcomm: %s", str(self))

        # skip games with only one (or less) log files
        if len(players) <= 1:
            self.__log().info("Only one log file available, can't sync!")
            return

        # select an already synced player or arbitrarily select the first of the players dict
        try:
            player_number, player = next(filter(lambda i, p: p['synced'], players.items()))
        except:
            player_number, player = next(iter(players.items()))

        # get the syncing point
        point = self.logs[player['key']].find_first_ready_state()
        if point is None:
            # if ready state not found, just use the first frame as syncing point
            point = (player['reader'][1]['FrameInfo'].frameNumber, player['reader'][1]['FrameInfo'].time)

        if not player['synced']:
            # save the sync info
            self.logs[player['key']].set_sync_point(point[1] / 1000.0)
            player['synced'] = True

        # iterate over the frames of the synchronizing player
        for frame in player['reader']:
            if 'TeamMessage' in frame:
                # iterate through frame messages
                for d in frame['TeamMessage'].data:
                    # ... and find the message of an un-synchronized player
                    if d.playerNum != player_number and d.playerNum in players and not players[d.playerNum]['synced']:
                        # a player is skipped, if the syncing message was found or if we're sure, that it can not be found any more
                        skip_player = False
                        # ... iterate over those players frames and try to find the send message (received by the synchronizing player)
                        for ff in players[d.playerNum]['reader']:
                            if 'TeamMessage' in ff:
                                for dd in ff['TeamMessage'].data:
                                    # found the correct player
                                    if dd.playerNum == d.playerNum:
                                        # found the correct players message
                                        # some old logs have slightly different timestamps for the same message - was a bug! :(
                                        if abs(dd.user.timestamp - d.user.timestamp) <= 5:  # ms
                                            # save the sync info
                                            self.logs[players[d.playerNum]['key']].set_sync_point((ff['FrameInfo'].time - (frame['FrameInfo'].time - point[1])) / 1000.0)
                                            players[d.playerNum]['synced'] = True
                                            skip_player = True
                                            break

                                        if dd.user.timestamp > d.user.timestamp:
                                            skip_player = True
                                            break
                            # skip the player for this frame
                            if skip_player: break

            # found syncing infos for all log, can stop loop
            if all(map(lambda p: p['synced'], players.values())): break

    def get_player_log(self, number:int):
        for l in self.logs:
            if number == self.logs[l].player_number:
                return self.logs[l]
        return None

    def __repr__(self):
        """Returns the string representation of this game."""
        return "{} - {} vs. {} #{} [{}]".format(self.date.strftime('%d.%m.%Y, %H:%M'), self.team_1, self.team_2, self.half, len(self.logs))

