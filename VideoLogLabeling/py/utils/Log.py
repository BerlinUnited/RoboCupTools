import glob
import json
import logging
import math
import os
import re
import io

from parsers import BehaviorParser
from .Config import config


class Log:
    """Represents a log file of a game and its addtional informations."""

    def __init__(self, game, dir, data_dir):
        """Constructor. Initializes class variables and reads some basic informations of the log file."""
        self.game = game
        self.directory = dir
        self.data_directory = data_dir

        self.file = None
        self.sync_file = None
        self.info_file = None
        self.info_data = None
        self.labels = []

        self.player_number = 0
        self.nao = None
        self.robot = None

        self.parse_info()
        self.scan_data()

    def __get_file(self, key):
        """
        Convenience method,returns a path specified in the config and identified by :key:.

        :param key: the directory name of the log configuration :key:
        :return:    the full path for this :key:
        """
        return os.path.join(self.directory, config['log'][key])

    def __get_data_file(self, key):
        """
        Convenience method,returns a data path specified in the config and identified by :key:.

        :param key: the directory name of the log configuration :key:
        :return:    the full data path for this :key:
        """
        return os.path.join(self.data_directory, config['log'][key])

    def parse_info(self):
        """Sets the log file path and extracts player number, robot number and an robot id from the log path based on the
        configuration regular expression."""
        log_file = self.__get_file('name')
        if os.path.isfile(log_file):
            self.file = log_file

        m = re.match(config['log']['regex'], os.path.basename(self.directory))

        self.player_number = m.group(1)
        self.nao = m.group(2)
        self.robot = m.group(3)

    def scan_data(self):
        """Reads the info file of this log and retrieves all label files of this log."""
        if os.path.isdir(self.data_directory):
            # set the sync information
            # TODO: this is the 'old' syncing file - should be handled differently!?
            sync_file = self.__get_data_file('sync')
            if os.path.isfile(sync_file):
                self.sync_file = sync_file
                # TODO: parse this file?
            # set the info file of this log
            info_file = self.__get_data_file('info')
            if os.path.isfile(info_file): self.info_file = info_file
            self.__read_info_file()
            # retrieve all label files
            self.labels = glob.glob(self.data_directory+'/'+config['log']['labels'][0]+'*'+config['log']['labels'][1])

    def __read_info_file(self):
        """Reads the content of the info file or creates the default dict, if the info file doesn't exists."""
        if self.info_data is None and self.info_file is not None and os.path.isfile(self.info_file):
            self.info_data = json.load(io.open(self.info_file, 'r', encoding='utf-8'))
        else:
            self.info_data = {'parsed_actions': [], 'intervals': {}, 'start': 0, 'end': 0, 'sync': {}}

    def parsed_actions(self):
        """Returns the parsed actions of this log."""
        return self.info_data['parsed_actions']

    def has_syncing_info(self):
        """Returns True, if the syncing info is available, False otherwise."""
        return True if 'sync' in self.info_data and self.info_data['sync'] else False

    def sync_with_videos(self):
        """Syncs the log file with the game videos simply by setting the first ready state of the log file to the first
        ready state of the video."""
        # TODO: this can be better if we have more events for the video!
        #       Then we can determine the correct syncing point, based on the time intervals between the events in the
        #       video and log!
        if self.file:
            point = self.__find_first_ready_state(self.file)
            if point:
                for k,v in self.game.videos.items():
                    if 'events' in v and 'ready' in v['events'] and v['events']['ready']:
                        if 'sync' not in self.info_data: self.info_data['sync'] = {}
                        self.info_data['sync'][k] = { "log": point[1]/1000.0, "video": v['events']['ready'][0] }
                self.__save_info_data()
            else:
                logging.getLogger('Log').warning("There's no ready state in this log file (%s)!", self.file)

    def create_old_syncing_file(self):
        """
        Syncs the log file with the game videos simply by setting the first ready state of the log file to the first
        ready state of the video. Therefore a sync file is created.

        NOTE: This is the old syncing variant and should be deprecated.
        """
        if self.file:
            point = self.__find_first_ready_state()
            if point:
                self.__create_data_directory()
                self.sync_file = self.__get_data_file('sync')
                with open(self.sync_file, 'w') as sf:
                    sf.writelines([
                        '# generated by python script\n'
                        'sync-time-video=0.0\n',
                        'sync-time-log='+str(point[1]/1000.0)+'\n',
                        'video-file='+(list(self.game.videos.values())[0]['sources'][0] if self.game.videos else '')+'\n'
                    ])
            else:
                logging.getLogger('Log').warning("There's no ready state in this log file (%s)!", self.file)

    def __find_first_ready_state(self):
        """
        Retrieves the first ready state from the log file.

        :return:    tuple of frame numbe and frame time, if ready state was found, otherwise returns None
        """
        parser = BehaviorParser.BehaviorParser()
        log = BehaviorParser.LogReader(self.file, parser)

        for frame in log:
            if 'BehaviorStateComplete' in frame.messages:
                m, o = frame["BehaviorStateComplete"]
            else:
                m, o = frame["BehaviorStateSparse"]

            if m['game.state'] == 1:
                # read before closing log
                n = frame.number
                t = frame['FrameInfo'].time
                # close log
                log.close()
                return (n, t)

        return None

    def has_info_file(self):
        """
        Returns True, if info file is available, False otherwise.

        :return:    True|False
        """
        return self.info_file is not None

    def has_label_files(self):
        """
        Returns True, if at least one label file is available, False otherwise.

        :return:    True|False
        """
        return len(self.labels) > 0

    def create_info_file(self, actions):
        """Creates the logs info file. Therefore the log is parsed and the :actions: functions are applied to each parsed
        frame. After parsing the resulting info  are saved to the info file."""
        parser = BehaviorParser.BehaviorParser()
        log = BehaviorParser.LogReader(self.file, parser)
        # update parsed actions
        self.info_data['parsed_actions'] = list(set(self.info_data['parsed_actions']) | set(actions.keys()))
        tmp = {}

        if log.size > 0:
            # ignore the first frame and set the second frame time as starting point of this log file
            self.info_data['start'] = log[1]["FrameInfo"].time / (1000.0 * 60) * 60

        # enforce the whole log being parsed (this is necessary for older game logs)
        for frame in log:
            s, o = (None, None)
            if "BehaviorStateComplete" in frame.messages:
                s, o = frame["BehaviorStateComplete"]
            if "BehaviorStateSparse" in frame.messages:
                s, o = frame["BehaviorStateSparse"]
            # enforce parsing FrameInfo
            fi = frame["FrameInfo"]

            # got valid data
            if s and o and fi:
                for a in actions:
                    # check if an action applies
                    if actions[a](s, o):
                        # begin an interval for this action
                        if a not in tmp or tmp[a] is None:
                            tmp[a] = { 'type': a,
                                       'frame': fi.frameNumber,
                                       'begin': fi.time / (1000.0 * 60) * 60,
                                       "pose": {"x": s["robot_pose.x"], "y": s["robot_pose.y"], "r": s["robot_pose.rotation"] * math.pi / 180},
                                       "ball": {"x": s["ball.position.field.x"], "y": s["ball.position.field.y"]} }
                        elif tmp[a]['frame'] == fi.frameNumber - 1:
                            # continue this action interval
                            tmp[a]['frame'] = fi.frameNumber
                    elif a in tmp and tmp[a] is not None:
                        # there's an open interval, close it
                        tmp[a]['end'] = fi.time / (1000.0 * 60) * 60
                        interval_id = '{}_{}'.format(tmp[a]['frame'], a)
                        self.info_data['intervals'][interval_id] = tmp[a]
                        del tmp[a]

            # update the time of the last frame
            if fi: self.info_data['end'] = fi.time / (1000.0 * 60) * 60

        self.__save_info_data()

        log.close()

    def __save_info_data(self):
        """Saves the info data to the info file and creates the parent directory if necessary."""
        self.__create_data_directory()
        info_file = self.__get_data_file('info')
        json.dump(self.info_data, open(info_file, 'w'), indent=4, separators=(',', ': '))

    def __create_data_directory(self):
        """Creates the data directory if necessary."""
        if not os.path.isdir(self.data_directory):
            os.mkdir(self.data_directory)

    def __repr__(self):
        """Returns the string representation of this log."""
        return "Nao{} #{}".format(self.nao, self.player_number)
