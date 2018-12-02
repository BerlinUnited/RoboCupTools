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
        self.sync_file_old = None
        self.info_file = None
        self.info_data = None
        self.labels = []

        self.player_number = 0
        self.nao = None
        self.robot = None

        self.parse_info()
        self.scan_data()

    def reload(self):
        self.info_data = None
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

    def __set_default_info_data(self):
        """Sets the default data for the info variable."""
        self.info_data = {'parsed_actions': [], 'intervals': {}, 'start': 0, 'end': 0}  #, 'sync': 0.0

    def parse_info(self):
        """Sets the log file path and extracts player number, robot number and an robot id from the log path based on the
        configuration regular expression."""
        log_file = self.__get_file('name')
        if os.path.isfile(log_file):
            self.file = log_file
        else:
            logging.getLogger('Log').debug("Missing log file (%s)!", log_file)

        m = re.match(config['log']['regex'], os.path.basename(self.directory))
        if m:
            self.player_number = m.group(1)
            self.nao = m.group(2)
            self.robot = m.group(3)
        else:
            logging.getLogger('Log').debug("Log directory doesn't match regex (%s)!", self.directory)

    def scan_data(self):
        """Reads the info file of this log and retrieves all label files of this log."""
        if os.path.isdir(self.data_directory):
            # set the OLD sync information
            sync_file_old = self.__get_data_file('sync')
            if os.path.isfile(sync_file_old):
                self.sync_file_old = sync_file_old
            # set the info file of this log
            info_file = self.__get_data_file('info')
            if os.path.isfile(info_file): self.info_file = info_file
            self.__read_info_file()
            # retrieve all label files
            self.labels = glob.glob(self.data_directory+'/'+config['log']['labels'][0]+'*'+config['log']['labels'][1])
        else:
            logging.getLogger('Log').debug("Data directory doesn't exist (%s)!", self.data_directory)
            self.__set_default_info_data()

    def __read_info_file(self):
        """Reads the content of the info file or creates the default dict, if the info file doesn't exists."""
        if self.info_data is None:
            if self.info_file is not None and os.path.isfile(self.info_file):
                logging.getLogger('Log').debug("Read log's info file (%s).", self.info_file)
                self.info_data = json.load(io.open(self.info_file, 'r', encoding='utf-8'))
            else:
                logging.getLogger('Log').debug("No log info file available (%s)!", self.info_file)
                self.__set_default_info_data()

    def parsed_actions(self):
        """Returns the parsed actions of this log."""
        return self.info_data['parsed_actions']

    def has_syncing_info(self):
        """Returns True, if the syncing info is available, False otherwise."""
        return True if 'sync' in self.info_data else False

    def has_syncing_info_old(self):
        """Returns True, if the old syncing info is available, False otherwise."""
        return self.sync_file_old is not None

    def set_sync_point(self, time:float):
        self.info_data['sync'] = time
        self.__save_info_data()

    def sync_with_videos_old(self):
        """
        Syncs the log file with the game videos simply by setting the first ready state of the log file to the first
        ready state of the video. Therefore a sync file is created.

        NOTE: This is the old syncing variant and should be deprecated.
        """
        if self.file:
            # if there's still no sync info, it couldn't found some
            if self.has_syncing_info():
                self.__create_data_directory()
                # take the first video to create the old sync file
                k,s = list(self.info_data['sync'].items())[0]
                v = self.game.videos[k]
                self.sync_file_old = self.__get_data_file('sync')
                with open(self.sync_file_old, 'w') as sf:
                    sf.writelines([
                        '# generated by python script\n'
                        'sync-time-video='+str(s['video'])+'\n',
                        'sync-time-log='+str(s['log'])+'\n',
                        'video-file='+v['sources'][0]+'\n'
                    ])
            else:
                logging.getLogger('Log').warning("Couldn't create old syncing file - no syncing info available.")

    def find_first_ready_state(self):
        """
        Retrieves the first ready state from the log file.

        :return:    tuple of frame number and frame time, if ready state was found, otherwise returns None
        """
        # get all ready states of the already parsed log file
        ready = self.get_action('ready')
        # are the ready states?
        if ready:
            # return the first ready state of this log file
            logging.getLogger('Log').debug("Use already parsed ready state for retrieving first one.")
            ready.sort(key=lambda i: i['frame'])
            return (ready[0]['frame'], ready[0]['begin']*1000.0)

        # ready state not parsed yet - find them
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
            self.info_data['start'] = log[1]["FrameInfo"].time / 1000.0

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
                                       'begin': fi.time / 1000.0,
                                       "pose": {"x": s["robot_pose.x"], "y": s["robot_pose.y"], "r": s["robot_pose.rotation"] * math.pi / 180},
                                       "ball": {"x": s["ball.position.field.x"], "y": s["ball.position.field.y"]} }
                        elif tmp[a]['frame'] == fi.frameNumber - 1:
                            # continue this action interval
                            tmp[a]['frame'] = fi.frameNumber
                    elif a in tmp and tmp[a] is not None:
                        # there's an open interval, close it
                        tmp[a]['end'] = fi.time / 1000.0
                        interval_id = '{}_{}'.format(tmp[a]['frame'], a)
                        self.info_data['intervals'][interval_id] = tmp[a]
                        del tmp[a]

            # update the time of the last frame
            if fi: self.info_data['end'] = fi.time / 1000.0

        self.__save_info_data()

        log.close()

    def __save_info_data(self):
        """Saves the info data to the info file and creates the parent directory if necessary."""
        self.__create_data_directory()
        logging.getLogger('Log').debug("Save log info file (%s)!", self.data_directory)
        info_file = self.__get_data_file('info')
        json.dump(self.info_data, open(info_file, 'w'), indent=4, separators=(',', ': '))

    def __create_data_directory(self):
        """Creates the data directory if necessary."""
        if not os.path.isdir(self.data_directory):
            logging.getLogger('Log').debug("Create data directory for log (%s)!", self.data_directory)
            os.makedirs(self.data_directory)

    def get_action(self, key:str):
        """
        Returns all action intervals with type :key:.
        An empty list could mean, that there's no action of :key: or it wasn't parsed yet!

        :param key: the action type
        :return:    a list of intervals found in this log file
        """
        result = []
        for a in self.info_data['intervals']:
            if self.info_data['intervals'][a]['type'] == key:
                result.append(self.info_data['intervals'][a])
        return result

    def __repr__(self):
        """Returns the string representation of this log."""
        return "Nao{} #{}".format(self.nao, self.player_number)
