import logging
import os
import re
import queue
import sqlite3
import threading
import socket
import time
import json
import zmq

from services import Messages
from services.data.GameControlData import GameControlData
from utils.Configuration import Configuration


class GameLogger(threading.Thread):
    def __init__(self, context: zmq.Context, mq_port: int, logger: logging.Logger = None):
        super().__init__()

        self._logger = logging.getLogger(self.logger_name) if logger is None else logger.getChild(self.logger_name)
        self.__cancel = threading.Event()

        self.__sub = context.socket(zmq.SUB)  # type: zmq.Socket
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GoProStatus.key)
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GameControllerMessage.key)
        self.__sub.connect(f"tcp://localhost:{mq_port}")

    @property
    def logger_name(self):
        return self.__class__.__name__

    def wait(self):
        self.__cancel.wait()

    def stop(self):
        self.__cancel.set()

    def run(self):
        self._logger.info('Start GameLogger')
        poller = zmq.Poller()
        poller.register(self.__sub, zmq.POLLIN)
        # run until canceled
        while not self.__cancel.is_set():
            try:
                # Poll for events, timeout set to 500 milliseconds (0.5 second)
                if poller.poll(500):
                    topic, message = self.__sub.recv_multipart()
                    if topic == Messages.GoProStatus.key:
                        self._handle_gopro(json.loads(message))
                    elif topic == Messages.GameControllerMessage.key:
                        self._handle_gamecontroller(GameControlData(message))
                    else:
                        self._logger.warning('Unknown topic')
            except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                self.stop()
        self._close_log()
        self.__sub.close()
        self._logger.debug("GameLogger thread finished.")

    def _handle_gopro(self, gopro):
        pass

    def _handle_gamecontroller(self, gc_data):
        pass

    def _close_log(self):
        pass


class GameLoggerLog(GameLogger):

    def __init__(self, context: zmq.Context, mq_port: int, directory, teams=None, log_invisible=False, logger: logging.Logger = None):
        super().__init__(context, mq_port, logger=logger)

        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.teams = teams if teams is not None else {}
        self.log_invisible = log_invisible
        self.messages = queue.Queue()

        self.state = {'t1': None, 't2': None, 'h': None, 'v': None}
        self.last_file = None
        self.added_video = False

        self.extension = '.log'
        self.separator = ', '
        self.raspi_name = socket.gethostname()
        self.gopro_info = 'Unknown'

        self.__last_gopro = None
        self.__last_gc_data = None  # type: GameControlData|None

    def _handle_gopro(self, gopro):
        # check, whether the gopro stopped recording and got a new video file
        if gopro is not None:
            self.__last_gopro = gopro  # remember last gopro status
            if gopro['state'] == 2 and self.state['v'] != gopro['lastVideo']:
                if self.last_file is not None:
                    # got a videofile, add it to the game
                    self._logger.debug("new video file: " + gopro['lastVideo'])
                    # if there was already a video written to the log file, add seperator first
                    if self.added_video: self.last_file.write(self.separator)
                    # remember, that a video was already added
                    else: self.added_video = True
                    # write the video name to the log file
                    self.last_file.write(json.dumps(gopro['lastVideo']))
                    self.last_file.flush()
                    self.state['v'] = gopro['lastVideo']
                else:
                    self._logger.error("Got a video file, but without an running game (%s)!", gopro['lastVideo'])
                    # prevent printing error message multiple times
                    self.state['v'] = gopro['lastVideo']

    def _handle_gamecontroller(self, gc_data):
        # check data of the gamecontroller
        if gc_data is not None:
            # check game file - did something changed in the game state?
            if self.__gamestate_changed(gc_data):
                # close previous/old game file
                self._close_log()
                # remember current state
                self.state['t1'] = gc_data.team[0].teamNumber
                self.state['t2'] = gc_data.team[1].teamNumber
                self.state['h']  = gc_data.firstHalf
                # if we shouldn't log games with invisibles and there's one, skip this game
                if self.log_invisible or (gc_data.team[0].teamNumber != 0 and gc_data.team[1].teamNumber != 0):
                    # replace whitespaces with underscore
                    t1 = self.__get_team(gc_data.team[0].teamNumber)
                    t2 = self.__get_team(gc_data.team[1].teamNumber)
                    t = t1 + '_vs_' + t2 if gc_data.firstHalf else t2 + '_vs_' + t1
                    h = '1stHalf' if gc_data.firstHalf else '2ndHalf'
                    # open new game file
                    file = self.directory + "_".join([time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()), t, h, self.raspi_name]) + self.extension
                    # append, if already exists
                    self.last_file = open(file, 'a')
                    if self.last_file:
                        self._logger.debug("created new log file: " + file)
                        # make sure everybody can read/write the file
                        os.chmod(self.last_file.name, 0o666)
                        self.last_file.write('{ "video": [')
                        self.last_file.flush()
            # remember last gc data
            self.__last_gc_data = gc_data
        else:
            # no gamecontroller / timed out? - close log
            self._close_log()

    def __gamestate_changed(self, gc_data):
        return self.last_file is None \
            or self.state['t1'] != gc_data.team[0].teamNumber \
            or self.state['t2'] != gc_data.team[1].teamNumber \
            or self.state['h'] != gc_data.firstHalf

    def __get_team(self, team):
        return re.sub("\s+", "_", str(self.teams[team] if team in self.teams else self.teams[str(team)] if str(team) in self.teams else team))

    def _close_log(self):
        if self.last_file is not None:
            self.last_file.write('], "info": {}, "gopro_time": "{}" }}\n'.format(
                json.dumps(self.__last_gopro['info'] if self.__last_gopro else {}),
                self.__last_gopro['datetime'] if self.__last_gopro else ''
            ))
            self.last_file.close()
            self._logger.debug("closed log file: " + self.last_file.name)
            self.last_file = None
            self.added_video = False


class GameLoggerSql(GameLogger):

    def __init__(self, context: zmq.Context, mq_port: int, db, teams=None, logger: logging.Logger = None):
        super().__init__(context, mq_port, logger=logger)

        self.db = db
        self.teams = teams if teams is not None else {}
        self.maxTimeGameValid = 60*30

        self.state = {'v': None}
        self.last_id = 0

        self.__con = None  # type: sqlite3.Connection|None
        self.__init_database()

    def _handle_gopro(self, gopro):
        if gopro is not None and gopro['state'] == 2 and self.state['v'] != gopro['lastVideo']:
            # got a videofile, add it to the game entry
            self.__open_database()
            self.__con.cursor().execute("UPDATE game SET video = video || ? WHERE id = ?",
                                        [str(gopro['lastVideo']) + ', ', self.last_id])
            self.__con.commit()

    def _handle_gamecontroller(self, gc_data):
        if gc_data is not None:
            self.__open_database()
            ts = int(time.time())
            # check&get game id
            db_id = self.__con.cursor().execute(
                "SELECT id FROM game WHERE timestmap >= ? and phase = ? and type = ? and half = ? and team_1 = ? and team_2 = ?",
                [ts-self.maxTimeGameValid, gc_data.competitionPhase, gc_data.competitionType, gc_data.firstHalf, gc_data.team[0].teamNumber, gc_data.team[1].teamNumber]
            ).fetchone()
            if not db_id:
                # new game
                self.__con.cursor().execute(
                    "INSERT INTO game (timestmap, phase, type, half, team_1, team_1_name, team_2, team_2_name) VALUES (?,?,?,?,?,?,?,?)",
                    [ts, gc_data.competitionPhase, gc_data.competitionType, gc_data.firstHalf, gc_data.team[0].teamNumber, self.teams[gc_data.team[0].teamNumber] if gc_data.team[0].teamNumber in self.teams else None, gc_data.team[1].teamNumber, self.teams[gc_data.team[1].teamNumber] if gc_data.team[1].teamNumber in self.teams else None]
                )
                self.__con.commit()
                db_id = self.__con.cursor().lastrowid
            else:
                db_id = db_id[0]

            if db_id is not None:
                self.last_id = db_id
                if db_id not in self.state:
                    # didn't have something about the current game - init
                    self.state[db_id] = {'phase': gc_data.gamePhase, 'state': gc_data.gameState, 'set': gc_data.setPlay, 'half': gc_data.firstHalf, 'score': (gc_data.team[0].score, gc_data.team[1].score)}
                else:
                    # game phase change
                    if self.state[db_id]['phase'] != gc_data.gamePhase:
                        self.__con.cursor().execute(
                            "INSERT INTO event (timestmap, game_id, type, time, extra) VALUES (?,?,?,?,?)",
                            [ts, db_id, 'phase_change', gc_data.secsRemaining, '[{}, {}]'.format(self.state[db_id]['phase'], gc_data.gamePhase)]
                        )
                        self.state[db_id]['phase'] = gc_data.gamePhase
                    # game state change
                    if self.state[db_id]['state'] != gc_data.gameState:
                        self.__con.cursor().execute(
                            "INSERT INTO event (timestmap, game_id, type, time, extra) VALUES (?,?,?,?,?)",
                            [ts, db_id, 'state_change', gc_data.secsRemaining, '[{}, {}]'.format(self.state[db_id]['state'], gc_data.gameState)]
                        )
                        self.state[db_id]['state'] = gc_data.gameState
                    # free kick
                    if self.state[db_id]['set'] != gc_data.setPlay:
                        # only log the beginning of the free kick
                        if self.state[db_id]['set'] == 0:
                            self.__con.cursor().execute(
                                "INSERT INTO event (timestmap, game_id, type, time, extra) VALUES (?,?,?,?,?)",
                                [ts, db_id, 'free_kick', gc_data.secsRemaining, str(gc_data.kickingTeam)]
                            )
                        self.state[db_id]['set'] = gc_data.setPlay
                    # goal scored
                    if self.state[db_id]['score'][0] != gc_data.team[0].score or self.state[db_id]['score'][1] != gc_data.team[1].score:
                        self.__con.cursor().execute(
                            "INSERT INTO event (timestmap, game_id, type, time, extra) VALUES (?,?,?,?,?)",
                            [ts, db_id, 'goal', gc_data.secsRemaining, '[{}, {}]'.format(gc_data.team[0].score, gc_data.team[1].score)]
                        )
                        self.state[db_id]['score'] = (gc_data.team[0].score, gc_data.team[1].score)

    def _close_log(self):
        self.__close_database()

    def __init_database(self):
        self.__open_database()
        self.__con.execute("""
            CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestmap INTEGER,
                phase INTEGER,
                type INTEGER,
                half INTEGER,
                team_1 INTEGER,
                team_1_name VARCHAR(50),
                team_2 INTEGER,
                team_2_name VARCHAR(50),
                video TEXT DEFAULT ''
            );""")
        self.__con.execute("""
            CREATE TABLE IF NOT EXISTS event (
                timestmap INTEGER,
                game_id INTEGER,
                type VARCHAR(20),
                time INTEGER,
                extra TEXT,
                PRIMARY KEY (timestmap, game_id, type),
                FOREIGN KEY (game_id) REFERENCES game (id) ON DELETE CASCADE ON UPDATE NO ACTION
            );""")
        self.__close_database()

    def __open_database(self):
        if self.__con is None:
            self.__con = sqlite3.connect(self.db)

    def __close_database(self):
        if self.__con is not None:
            self.__con.commit()
            self.__con.close()
            self.__con = None


def main(ctx: zmq.Context = None, config: Configuration = None):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    #log = GameLoggerSql(ctx, _config.bus.port_recv, './logs/gamelog.db')
    _log = GameLoggerLog(context=_ctx,
                         mq_port=_config.bus.port_recv,
                         directory=_config.gl.log_directory,
                         teams=_config.teams,
                         log_invisible=_config.gl.log_invisible,
                         logger=_config.logger())

    try:
        _log.run()
    except (KeyboardInterrupt, SystemExit) as e:
        pass

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main()
