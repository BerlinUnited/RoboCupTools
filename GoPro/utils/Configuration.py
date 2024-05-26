import dataclasses
import logging
import os
import sys


@dataclasses.dataclass
class MessageBus:
    port_send: int = 5560
    port_recv: int = 5559
    monitor: bool = False


@dataclasses.dataclass
class GoPro:
    cli: bool = False
    quiet: bool = False
    ignore: bool = False
    max_time: int = 900
    rec_invisible: bool = False
    # for older GoPro, which are controlled via Wi-Fi
    device: str = 'wifi0'
    ssid: str = None
    passwd: str = None
    ble_mac: str = None


@dataclasses.dataclass
class GameLogger:
    log_directory: str = './logs/'
    log_invisible: bool = False


@dataclasses.dataclass
class GameController:
    source: str = None
    port: int = 3838
    true_data: bool = True
    true_data_port: int = 3636


@dataclasses.dataclass
class Webserver:
    http_port: int = 8080
    ws_port: int = 8081


@dataclasses.dataclass
class Logger:
    _instance = logging.getLogger('GoPi')
    level: str = 'DEBUG'
    syslog: bool = False
    directory: str = None

    def __call__(self, *args, **kwargs):
        return self._instance

    class DuplicateFilter(logging.Filter):
        def __init__(self):
            super().__init__()
            self.last_log = None
            self.last_cnt = 0

        def filter(self, record: logging.LogRecord):
            # make sure my own messages gets logged without interfering with other messages
            if os.path.splitext(os.path.basename(__file__))[0] == record.module:
                return True
            # the current log record
            current_log = (record.module, record.levelno, record.msg)
            current_cnt = self.last_cnt
            # did the record change in comparison to the last?
            if current_log != self.last_log:
                # reset count before logging the 'informational' message
                self.last_cnt = 0
                # if the last message was logged multiple times, log that info
                if current_cnt != 0:
                    pass
                    #logger.log(self.last_log[1], "The last message occurred %d times", current_cnt)
                # set the new message
                self.last_log = current_log
                return True
            # update same message counter
            self.last_cnt += 1
            return False

    class Formatter(logging.Formatter):
        def __init__(self, format: str, child_format: str, include_date: bool = False):
            super().__init__(format)
            self._include_date = include_date
            self._format = format
            self._child_format = child_format

        def format(self, record):
            prefix = self.formatTime(record) + ' ' if self._include_date else ''
            if record.name != 'GoPi':
                self._style._fmt = prefix + self._child_format
            else:
                self._style._fmt = prefix + self._format
            return logging.Formatter.format(self, record)  # super(LogFormatter, self).format(format)


class Configuration:
    bus = MessageBus()
    gopro = GoPro()
    gc = GameController()
    gl = GameLogger()
    logger = Logger()
    web = Webserver()
    teams: dict[int, str] = dict()

    def __init__(self, file: str = 'config.ini'):
        self.__file = file

        if self.__file and os.path.exists(self.__file):
            self.__init_file_config()
        else:
            print('Config file not found:', file)

        self.__init_logging()

    def __init_logging(self):
        import logging.handlers

        format = '[%(levelname)s]: %(message)s'
        child_format = '[%(levelname)s] %(name)s: %(message)s'

        lvl = self.logger.level if isinstance(self.logger.level, int) else logging.getLevelName(self.logger.level)
        if not isinstance(lvl, int):
            lvl = logging.WARNING
            self.logger().warning('Invalid log level, fall back to WARNING')

        logging.basicConfig(level=lvl, format=format)
        self.logger().propagate = False

        sh = logging.StreamHandler()
        sh.setFormatter(Logger.Formatter(format, child_format))
        self.logger().addHandler(sh)

        if self.logger.syslog:
            sh = logging.handlers.SysLogHandler(address='/dev/log')
            sh.setFormatter(logging.Formatter(f'{self.logger().name}:{format}'))
            self.logger().addHandler(sh)

        if self.logger.directory:
            # log to files by day and only warning and above
            log = os.path.join(self.logger.directory, self.logger().name + '.log')
            fh = logging.handlers.TimedRotatingFileHandler(log, 'D', backupCount=5)
            fh.setLevel(logging.WARNING)
            fh.setFormatter(Logger.Formatter(format, child_format, True))
            fh.addFilter(Logger.DuplicateFilter())
            self.logger().addHandler(fh)

    def __init_file_config(self):
        if self.__file.endswith('.json'):
            self.__init_file_config_json()
        elif self.__file.endswith('.ini'):
            self.__init_file_config_ini()
        elif self.__file.endswith('.toml'):
            self.__init_file_config_toml()

    def __init_file_config_json(self):
        import json
        with open(self.__file, mode='r') as f:
            self.__init_config(json.load(f))

    def __init_file_config_ini(self):
        import configparser
        cp = configparser.ConfigParser()
        cp.read(self.__file)
        self.__init_config({s: dict(cp.items(s)) for s in cp.sections()})

    def __init_file_config_toml(self):
        if sys.version_info >= (3, 11):
            import tomllib
            with open("pyproject.toml", "rb") as f:
                self.__init_config(tomllib.load(f))
        else:
            print('TOML config files are supported with python 3.11+')

    def __init_config(self, values: dict):
        for k in values:
            if hasattr(self, k):
                cc = getattr(self, k)

                if dataclasses.is_dataclass(cc):
                    for a in values[k]:
                        if hasattr(cc, a):
                            vv = getattr(cc, a)
                            try:
                                if isinstance(vv, bool):
                                    setattr(cc, a, values[k][a].upper() == 'TRUE')
                                elif isinstance(vv, int):
                                    setattr(cc, a, int(values[k][a]))
                                else:
                                    setattr(cc, a, values[k][a])
                            except:
                                print(f'Unable to apply configuration {a} of type {type(vv)} with value {values[k][a]}')
                else:
                    setattr(self, k, values[k])

    def __str__(self):
        return str({
            'bus': self.bus,
            'gopro': self.gopro,
            'gc': self.gc,
            'gl': self.gl,
            'logger': self.logger,
            'teams': self.teams
        })


if __name__ == '__main__':
    c = Configuration(os.path.join(os.path.dirname(__file__), '../config.ini'))
    print(c)
