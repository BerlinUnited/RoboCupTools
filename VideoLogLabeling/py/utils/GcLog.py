import glob
import io
import json
import logging
import os
import subprocess

from .Config import config


class GcLog:
    """Represents a gamecontroller log file and its converted parts."""

    def __init__(self, file, data_dir):
        """Constructor, Searches for converted log files."""
        self.file = file
        self.data_directory = data_dir

        self.reload()


    def reload(self):
        # reset class variables
        self.info_file = None
        self.info_data = None
        self.__data = None
        self.converted = {}

        # search for converted gamecontroller log files
        for c in glob.glob(self.file + '*' + config['gc']['conv_ext']):
            # use the part between the log file name and the converted extension as identifier for the converted file
            _ = c[len(self.file):-len(config['gc']['conv_ext'])].strip('.')
            self.converted[_] = c
        if not self.converted:
            logging.getLogger(__class__.__name__).debug("There are unconverted gamecontroller log files.")
        elif 'gtc' not in self.converted:
            logging.getLogger(__class__.__name__).debug("The 'gtc' converted gamecontroller log file is required.")

        # check gamecontroller info file
        info_file = os.path.join(self.data_directory, config['gc']['file'])
        if os.path.isfile(info_file):
            self.info_file = info_file
        #
        self.__read_info_file()

    def __read_info_file(self):
        """Reads the content of the info file or creates the default dict, if the info file doesn't exists."""
        if self.info_data is None and self.info_file is not None and os.path.isfile(self.info_file):
            logging.getLogger(__class__.__name__).debug("Read gamecontroller info file (%s).", self.info_file)
            self.info_data = json.load(io.open(self.info_file, 'r', encoding='utf-8'))
        else:
            logging.getLogger(__class__.__name__).debug("No gamecontroller info file available (%s)!", self.file)
            self.info_data = { 'parsed_actions': [], 'intervals': {}, 'sync': 0.0 }

    def has_converted(self):
        """
        Returns True, if a gamecontroller log file is converted to json, otherwise False.

        :return:    True|False
        """
        return True if self.converted else False

    def is_converted(self):
        return 'gtc' in self.converted

    def convert(self, converter:str):
        """
        Converts the gamecontroller log file with the given converter command.

        :param converter:   the java gamecontroller log file converter
        :return:    None
        """
        if self.file:
            logging.getLogger(__class__.__name__).debug("Converting gamecontroller log file %s", self.file)
            result = subprocess.run(['java', '-jar', converter, self.file] + config['gc']['conv_options'], stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)
            if result.returncode != 0:
                logging.getLogger(__class__.__name__).error("An error occurred while converting gamecontroller logs:\n%s", result.stderr)
            else:
                logging.getLogger(__class__.__name__).debug("Converted gamecontroller log file")

    def has_info_file(self):
        return self.info_file is not None

    def create_info_file(self, actions):
        # load converted gamecontroller log file
        self.__read_log()
        if self.__data:
            tmp = {}
            # iterate over messages from the gamecontroller log file
            for msg in self.__data:
                # execute each action
                for a_name in actions:
                    if actions[a_name](msg):
                        # begin an interval for this action
                        if a_name not in tmp or tmp[a_name] is None:
                            tmp[a_name] = { 'type': a_name, 'begin': msg['timestamp'], 'end': msg['timestamp'] }
                        else:
                            tmp[a_name]['end'] = msg['timestamp']
                    elif a_name in tmp and tmp[a_name] is not None and tmp[a_name]['end'] + 1000 < msg['timestamp']:
                        # there's an open interval, close it, if it didn't got updated over 1 second
                        interval_id = '{}_{}'.format(tmp[a_name]['begin'], a_name)
                        self.info_data['intervals'][interval_id] = tmp[a_name]
                        del tmp[a_name]
            # update parsed actions
            self.info_data['parsed_actions'] = list(set(self.info_data['parsed_actions']) | set(actions.keys()))
            # close open intervals
            for t in tmp:
                interval_id = '{}_{}'.format(tmp[t]['begin'], t)
                self.info_data['intervals'][interval_id] = tmp[t]

        self.__save_info_data()

    def __read_log(self):
        if self.__data is None and 'gtc' in self.converted:
            self.__data = json.load(io.open(self.converted['gtc'], 'r', encoding='utf-8'))

    def data(self):
        self.__read_log()
        return self.__data

    def set_sync_point(self, time):
        self.info_data['sync'] = time
        self.__save_info_data()

    def __save_info_data(self):
        """Saves the info data to the info file and creates the parent directory if necessary."""
        self.__create_data_directory()
        logging.getLogger(__class__.__name__).debug("Save gamecontroller info file (%s)!", self.data_directory)
        info_file = os.path.join(self.data_directory, config['gc']['file'])
        json.dump(self.info_data, open(info_file, 'w'), indent=4, separators=(',', ': '))

    def __create_data_directory(self):
        """Creates the data directory if necessary."""
        if not os.path.isdir(self.data_directory):
            logging.getLogger(__class__.__name__).debug("Create data directory for gamecontroller info file (%s)!", self.data_directory)
            os.mkdir(self.data_directory)

    def parsed_actions(self):
        """Returns the parsed actions of this log."""
        return self.info_data['parsed_actions']
