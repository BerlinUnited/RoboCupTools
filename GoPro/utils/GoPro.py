import datetime
import threading
import time
import traceback
from abc import ABCMeta, abstractmethod

from utils import Logger, blackboard
from utils.GameControlData import GameControlData

# setup logger for network related logs
logger = Logger.getLogger("GoPro")


class GoPro(threading.Thread, metaclass=ABCMeta):

    class Settings:
        FRAME_RATE = 'FRAME_RATE'

        class FrameRate:
            FR_24 = 24
            FR_25 = 25
            FR_30 = 30
            FR_48 = 48
            FR_50 = 50
            FR_60 = 60
            FR_100 = 100
            FR_120 = 120
            FR_240 = 240

        FOV = 'FOV'

        class Fov:
            LINEAR = 'linear'
            NARROW = 'narrow'
            MEDIUM = 'medium'
            WIDE = 'wide'
            SV = 'sv'

        RESOLUTION = 'RESOLUTION'

        class Resolution:
            R_4K = '4K'
            R_2K = '2K'
            R_1440P = '1440p'
            R_1080P = '1080p'
            R_960P = '960p'
            R_720P = '720p'
            R_480P = '480p'

    class Modes:
        VIDEO = 'Video'
        PHOTO = 'Photo'

    def __init__(self, quiet: bool, ignore: bool, max_time: int, rec_invisible: bool = False):
        super().__init__()

        self.quiet = quiet
        self.ignore = ignore
        self.max_time = max_time
        self.rec_invisible = rec_invisible
        self.take_photo_when_idle = 0 # in seconds
        self.__photo_timestamp = 0

        self.cam = None
        self.__cam_status = {'recording': False, 'mode': None, 'lastVideo': None, 'sd_card': False, 'info': {}, 'datetime': None}
        self.cam_settings = {}
        self.__user_settings = {
            GoPro.Settings.FRAME_RATE: GoPro.Settings.FrameRate.FR_30,
            GoPro.Settings.FOV: GoPro.Settings.Fov.SV,
            GoPro.Settings.RESOLUTION: GoPro.Settings.Resolution.R_1080P
        }
        self.gc_data = GameControlData()

        blackboard['gopro'] = {'state': 0, 'info': None, 'lastVideo': None, 'datetime': None}

        self.__is_connected = False
        self.__cancel = threading.Event()

    @staticmethod
    def settings():
        return {
            GoPro.Settings.FRAME_RATE: [
                GoPro.Settings.FrameRate.FR_24,
                GoPro.Settings.FrameRate.FR_25,
                GoPro.Settings.FrameRate.FR_30,
                GoPro.Settings.FrameRate.FR_48,
                GoPro.Settings.FrameRate.FR_50,
                GoPro.Settings.FrameRate.FR_60,
                GoPro.Settings.FrameRate.FR_100,
                GoPro.Settings.FrameRate.FR_120,
                GoPro.Settings.FrameRate.FR_240,
            ],
            GoPro.Settings.FOV: [
                GoPro.Settings.Fov.LINEAR,
                GoPro.Settings.Fov.NARROW,
                GoPro.Settings.Fov.MEDIUM,
                GoPro.Settings.Fov.WIDE,
                GoPro.Settings.Fov.SV,
            ],
            GoPro.Settings.RESOLUTION: [
                GoPro.Settings.Resolution.R_4K,
                GoPro.Settings.Resolution.R_2K,
                GoPro.Settings.Resolution.R_1440P,
                GoPro.Settings.Resolution.R_1080P,
                GoPro.Settings.Resolution.R_960P,
                GoPro.Settings.Resolution.R_720P,
                GoPro.Settings.Resolution.R_480P
            ]
        }

    @property
    def is_connected(self):
        return self.__is_connected

    @property
    def is_canceled(self) -> bool:
        return self.__cancel.is_set()

    @property
    def is_recording(self) -> bool:
        return self._is_recording()

    @property
    def has_sdcard(self) -> bool:
        return self._has_sdcard()

    @property
    def mode(self) -> str:
        return self._mode()

    @property
    def datetime(self) -> datetime.datetime:
        return self._datetime()

    @property
    def datetime_str(self) -> str:
        return self._datetime().strftime('%d.%m.%y, %H:%M:%S')

    @property
    def last_video(self):
        return self._last_video()

    @property
    def fps(self):
        return self._fps()

    @property
    def fov(self):
        return self._fov()

    @property
    def res(self):
        return self._res()

    def run(self):
        # init game state
        previous_state = {'game': GameControlData.STATE_INITIAL, 'time': time.monotonic(), 'card': True}
        # run until canceled
        while not self.is_canceled:
            try:
                if self.connect():
                    # update internal cam status
                    if not self._update_status():
                        self.disconnect()  # disconnected?!?
                        continue
                    # handling recording state
                    self.__handle_recording(previous_state)
                    # take "keep alive" photo;
                    if self.__keep_alive_photo():
                        self.take_photo()
                    self.__handle_sdcard(previous_state)
                else:
                    #
                    self.disconnect()
            except Exception as ex:
                # something unexpected happen!?
                Logger.error("{}\n{}".format(str(ex), traceback.format_exc()))
        # if canceled, at least fire the disconnect event
        self.disconnect()
        logger.debug("GoPro thread finished.")

    def cancel(self):
        self.__cancel.set()

    def connect(self) -> bool:
        """
        Connects to the GoPro.
        This blocks until connection is successful or if the thread is canceled.
        :return:
        """
        # try to connect
        while not self.is_connected and not self.is_canceled:
            # get GoPro
            logger.info("Connecting to GoPro ...")

            self.__set_bb_state(1)  # GoproConnecting
            self._init()

            if self._update_status():
                self.__is_connected = True

                self.__set_bb_state(2)  # GoproConnected
                self.__set_bb_info(self._info())
                self.__set_bb_datetime(self.datetime_str)

                # set GoPro to video mode
                self._set_video_mode()
                self.__update_user_settings()

                # if cam already recording, raise event
                if self.is_recording:
                    self.__set_bb_state(4)  # GoproStartRecording
            else:
                self.disconnect()
                time.sleep(1)

        return self.is_connected

    def disconnect(self):
        if self.is_connected:
            logger.info("Disconnecting from GoPro ...")
            self._unset()
            self.__set_bb_state(0)  # GoproDisconnected
            self.__is_connected = False

    def startRecording(self):
        if self.is_connected:
            if self.mode != "Video":
                self._set_video_mode()

            self.__update_user_settings()

            logger.debug("Start recording")
            self.__set_bb_state(4)  # GoproStartRecording
            self.__set_bb_datetime(self.datetime_str)
            self._start_recording()

    def stopRecording(self):
        if self.is_connected:
            logger.debug("Stop recording")
            self._stop_recording()
            if not self._update_status():
                self.disconnect()  # disconnected?!?
                return
            self.__set_bb_lastvideo(self.last_video)
            self.__set_bb_state(2)  # GoproStopRecording
            self.__set_bb_datetime(self.datetime_str)

    def take_photo(self):
        """ Takes a photo, but only if not currently recording a video. """
        if self.is_recording:
            self.__photo_timestamp = time.monotonic()
        else:
            logger.debug("Take a picture")
            if self.connect():
                self.__photo_timestamp = time.monotonic()
                self._take_photo()
                # reset to video mode
                self._set_video_mode()
            else:
                logger.error("Not connected to cam!?")

    def __get_bb(self, key: str):
        return blackboard[key]

    def __get_bb_gc(self) -> GameControlData:
        return self.__get_bb('gamecontroller')

    def __set_bb(self, key: str, value):
        blackboard['gopro'][key] = value

    def __set_bb_state(self, state: int):
        self.__set_bb('state', state)

    def __set_bb_datetime(self, dt: str):
        self.__set_bb('datetime', dt)

    def __set_bb_info(self, info):
        self.__set_bb('info', info)

    def __set_bb_lastvideo(self, video: str):
        self.__set_bb('lastVideo', video)

    def __keep_alive_photo(self) -> bool:
        return self.take_photo_when_idle > 0 and self.__photo_timestamp + self.take_photo_when_idle < time.time()

    def __handle_sdcard(self, state):
        # update sd-card status on the blackboard
        if state['card'] and not self.has_sdcard:
            self.__set_bb_state(3)  # GoproNoSdcard
        elif not state['card'] and self.has_sdcard:
            self.__set_bb_state(2)  # GoproSdcardInserted
        state['card'] = self.has_sdcard

    def __handle_recording(self, previous_state):
        gc_data = self.__get_bb_gc()
        if gc_data is not None:
            # check if one team is 'invisible'
            both_teams_valid = all([t.teamNumber > 0 for t in gc_data.team]) or self.rec_invisible

            # handle output
            if not self.quiet:
                output = "%s | %s | game state: %s | %s" % (
                    self.mode, "RECORDING!" if self.is_recording else "Not recording", gc_data.getGameState(), gc_data.secsRemaining)
                print(output, flush=True)

            # handle game state changes
            if not self.ignore and gc_data.secsRemaining < -self.max_time:
                # only stop, if we're still recording
                if self.is_recording:
                    self.stopRecording()
            elif gc_data.gameState == GameControlData.STATE_SET and previous_state['time'] + self.max_time < time.monotonic():
                # too long in the set state, stop recording!
                if self.is_recording:
                    logger.debug("Stopped recording because we were too long in set")
                    self.stopRecording()
            elif self.has_sdcard and not self.is_recording and both_teams_valid and (
                    gc_data.gameState in [GameControlData.STATE_READY, GameControlData.STATE_SET, GameControlData.STATE_PLAYING]):
                self.startRecording()
            elif self.is_recording and not (
                    gc_data.gameState in [GameControlData.STATE_READY, GameControlData.STATE_SET, GameControlData.STATE_PLAYING]):
                self.stopRecording()

            # handle game changes
            if previous_state['game'] != gc_data.gameState:
                logger.debug("Changed game state to: %s @ %d", gc_data.getGameState(), time.time())
                previous_state['time'] = time.monotonic()

            previous_state['game'] = gc_data.gameState
        else:
            if self.is_recording:
                self.stopRecording()

        previous_state['game'] = GameControlData.STATE_INITIAL

    def setUserSettings(self, settings: dict):
        # check the settings first
        gopro_settings = self.settings()
        for s, v in settings.items():
            if s not in gopro_settings.keys():
                raise Exception('Unknown GoPro setting: ' + s)
            if v not in gopro_settings[s]:
                raise Exception('Invalid GoPro setting: ' + s + ' = ' + v)
            self.__user_settings[s] = v
        # apply settings, if connected
        if self.is_connected:
            self.__update_user_settings()

    def __update_user_settings(self):
        logger.debug("Set user video settings")

        if self.__user_settings[GoPro.Settings.FRAME_RATE] != self.fps:
            if not self._set_fps(self.__user_settings[GoPro.Settings.FRAME_RATE]):
                logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.FRAME_RATE + "'")
                self.__user_settings[GoPro.Settings.FRAME_RATE] = None

        if self.__user_settings[GoPro.Settings.FOV] != self.fov:
            if not self._set_fov(self.__user_settings[GoPro.Settings.FOV]):
                logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.FOV + "'")
                self.__user_settings[GoPro.Settings.FOV] = None

        if self.__user_settings[GoPro.Settings.RESOLUTION] != self.res:
            if not self._set_res(self.__user_settings[GoPro.Settings.RESOLUTION]):
                logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.RESOLUTION + "'")
                self.__user_settings[GoPro.Settings.RESOLUTION] = None

    @abstractmethod
    def _init(self):
        """
        Creates the internal state and connects to the GoPro.
        :return:
        """
        pass

    @abstractmethod
    def _unset(self):
        """
        Disconnects from the GoPro and reset the internal state.
        :return:
        """
        pass

    @abstractmethod
    def _info(self) -> dict:
        """
        Returns some infos about the GoPro.
        :return:
        """
        pass

    @abstractmethod
    def _mode(self):
        return 'unknown'

    @abstractmethod
    def _set_video_mode(self):
        """
        Sets the video mode of the GoPro
        :return:
        """
        pass

    @abstractmethod
    def _take_photo(self):
        """
        Takes a photo with the GoPro.
        :return:
        """
        pass

    @abstractmethod
    def _datetime(self) -> datetime:
        """
        Returns the date and time of the GoPro.
        :return:
        """
        return datetime.datetime.now()

    @abstractmethod
    def _is_recording(self) -> bool:
        """
        Indicates, whether the GoPro is recording (True) or not (False).
        :return:
        """
        return False

    @abstractmethod
    def _has_sdcard(self) -> bool:
        """
        Indicates, whether the GoPro has a sdcard inserted (True) or not (False).
        :return:
        """
        return False

    @abstractmethod
    def _update_status(self) -> bool:
        """
        Updates the internal status.
        This method is called regularly.
        :return:
        """
        return False

    @abstractmethod
    def _start_recording(self):
        """
        Starts video recording.
        :return:
        """
        pass

    @abstractmethod
    def _stop_recording(self):
        """
        Stops video recording.
        :return:
        """
        pass

    @abstractmethod
    def _last_video(self) -> str|None:
        """
        Returns the last recorded video or None, if there're no recordings.
        :return:
        """
        return None

    @abstractmethod
    def _fps(self) -> str:
        """
        Returns the current frame rate (FPS).
        :return:
        """
        return ''

    @abstractmethod
    def _set_fps(self, value) -> bool:
        """
        Sets the frame rate (FPS).
        :param value:
        :return:
        """
        return False

    @abstractmethod
    def _fov(self) -> str:
        """
        Returns the current field of view (FOV)
        :return:
        """
        return ''

    @abstractmethod
    def _set_fov(self, value) -> bool:
        """
        Sets the field of view.
        :param value:
        :return:
        """
        return False

    @abstractmethod
    def _res(self) -> str:
        """
        Returns the current resolution.
        :return:
        """
        return ''

    @abstractmethod
    def _set_res(self, value) -> bool:
        """
        Sets the resolution.
        :param value:
        :return:
        """
        return False
