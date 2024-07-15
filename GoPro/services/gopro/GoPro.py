import datetime
import logging
import threading
import time
import traceback
from typing import Union

import zmq
from abc import ABCMeta, abstractmethod

from services import Messages
from services.data.GameControlData import GameControlData


class GoPro(threading.Thread, metaclass=ABCMeta):

    class Settings:
        class FrameRate:
            FR_24 = 24
            FR_25 = 25
            FR_30 = 30
            FR_50 = 50
            FR_60 = 60
            FR_100 = 100
            FR_120 = 120
            FR_240 = 240

        class Fov:
            LINEAR = 'linear'
            NARROW = 'narrow'
            MEDIUM = 'medium'
            WIDE = 'wide'
            SV = 'sv'

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

    def __init__(self,
                 context: zmq.Context,
                 mq_send: int,
                 mq_recv: int,
                 quiet: bool,
                 ignore: bool,
                 max_time: int,
                 rec_invisible: bool = False,
                 update_interval: float = 0.5,
                 logger: logging.Logger = None):

        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)
        self.__quiet = quiet
        self.__ignore = ignore
        self.__max_time = max_time
        self.__rec_invisible = rec_invisible
        self.__update_interval = update_interval  # in seconds
        self.__keep_alive_interval = 30  # in seconds
        self.__keep_alive_timestamp = 0
        self.__recording_states = [
            GameControlData.STATE_STANDBY,
            GameControlData.STATE_READY,
            GameControlData.STATE_SET,
            GameControlData.STATE_PLAYING
        ]

        # the default GoPro settings
        self.__user_settings = {
            GoPro.Settings.FrameRate: GoPro.Settings.FrameRate.FR_30,
            GoPro.Settings.Fov: GoPro.Settings.Fov.SV,
            GoPro.Settings.Resolution: GoPro.Settings.Resolution.R_1080P
        }

        # init GoPro infos
        self.__gopro = {'state': Messages.GoProStatus.State.DISCONNECTED, 'info': None, 'lastVideo': None, 'datetime': None}

        self.__pub: zmq.Socket = context.socket(zmq.PUB)
        self.__pub.connect(f"tcp://localhost:{mq_send}")

        self.__sub: zmq.Socket = context.socket(zmq.SUB)
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GameController.key)
        self.__sub.connect(f"tcp://localhost:{mq_recv}")

        # vars handling execution
        self.__is_connected = False
        self._cancel = threading.Event()

        self.__gc = None
        self.__gc_recv = threading.Thread(target=self.__handle_gc)
        self.__gc_lock = threading.Lock()

    def __handle_gc(self):
        poller = zmq.Poller()
        poller.register(self.__sub, zmq.POLLIN)
        while not self._cancel.is_set():
            try:
                # Poll for events, timeout set to 500 milliseconds (0.5 second)
                if poller.poll(500):
                    topic, message = self.__sub.recv_multipart()  # type: bytes, bytes

                    with self.__gc_lock:
                        if topic == Messages.GameControllerMessage.key:
                            self.__gc = GameControlData(message)
                        elif topic == Messages.GameControllerShutdown.key or topic == Messages.GameControllerDisconnect.key:
                            self.__gc = None
            except zmq.error.ContextTerminated:
                self.cancel()  # if the context is terminated we're expected to leave

    def _publish(self, message: Messages.Message):
        try:
            self.__pub.send_multipart([message.key, message.value])
        except zmq.error.ContextTerminated:
            # ignore on stop otherwise something else happen
            if not self._cancel.is_set():
                raise

    @property
    def state(self):
        return self.__gopro

    @property
    def is_connected(self):
        return self.__is_connected

    @property
    def is_canceled(self) -> bool:
        return self._cancel.is_set()

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
        self.__gc_recv.start()
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
                    self.__handle_sdcard(previous_state)
                    self.__keep_alive()
                else:
                    #
                    self.disconnect()
                # we don't need as fast as possible, so pause a little bit
                self._cancel.wait(self.__update_interval)
            except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                self.cancel()
            except Exception as ex:
                # something unexpected happen!?
                self._logger.error("{}\n{}".format(str(ex), traceback.format_exc()))
        # if canceled, at least fire the disconnect event
        self.disconnect()
        self.__pub.close()
        self.__sub.close()
        self.__gc_recv.join()
        self._logger.debug("GoPro thread finished.")

    def cancel(self):
        self._cancel.set()

    def connect(self) -> bool:
        """
        Connects to the GoPro.
        This blocks until connection is successful or if the thread is canceled.
        :return:
        """
        # try to connect
        while not self.is_connected and not self.is_canceled:
            if self._connect() and self._update_status():
                self.__is_connected = True

                self._update(state=Messages.GoProStatus.State.CONNECTED, info=self._info(), dt=self.datetime_str)  # GoproConnected

                # set GoPro to video mode
                self._set_video_mode()
                self.__update_user_settings()

                # if cam already recording, raise event
                if self.is_recording:
                    self._update(state=Messages.GoProStatus.State.RECORDING)  # GoproStartRecording
            else:
                self.disconnect()
                self._cancel.wait(2)  # GoPro not found, wait before next attempt

        return self.is_connected

    def disconnect(self):
        if self.is_connected:
            self._logger.info("Disconnecting from GoPro ...")
            self._unset()
            self.__is_connected = False
        self._logger.info("Disconnected from GoPro ...")
        self._update(state=Messages.GoProStatus.State.DISCONNECTED)  # GoproDisconnected

    def startRecording(self):
        if self.is_connected:
            if self.mode != "Video":
                self._set_video_mode()

            self.__update_user_settings()

            self._logger.debug("Start recording")
            self._update(state=Messages.GoProStatus.State.RECORDING, dt=self.datetime_str)  # GoproStartRecording
            self._start_recording()

    def stopRecording(self):
        if self.is_connected:
            self._logger.debug("Stop recording")
            self._stop_recording()
            if not self._update_status():
                self.disconnect()  # disconnected?!?
                return
            self._update(state=Messages.GoProStatus.State.CONNECTED, video=self.last_video, dt=self.datetime_str)  # GoproStopRecording

    def take_photo(self):
        """ Takes a photo, but only if not currently recording a video. """
        if self.is_recording:
            self.__keep_alive_update()
        else:
            self._logger.debug("Take a picture")
            if self.connect():
                self._take_photo()
                self._set_video_mode()  # reset to video mode
                self.__keep_alive_update()
            else:
                self._logger.error("Not connected to cam!?")

    def _update(self, state: Messages.GoProStatus.State = None, info: dict = None, video: str = None, dt: str = None):
        # update internal state
        if state: self.__gopro['state'] = state.value
        if info:  self.__gopro['info'] = info
        if video: self.__gopro['lastVideo'] = video
        if dt:    self.__gopro['datetime'] = dt
        # ... and publish it
        self._publish(Messages.GoProStatus(self.__gopro))

    def __keep_alive(self):
        if self.__keep_alive_interval > 0 and self.__keep_alive_timestamp + self.__keep_alive_interval < time.monotonic():
            self._keep_alive()
            self.__keep_alive_update()
            self._update()  # with the keep alive send a periodic update of the current state

    def __keep_alive_update(self):
        self.__keep_alive_timestamp = time.monotonic()

    def __handle_sdcard(self, state):
        # update sd-card status on the blackboard
        if state['card'] and not self.has_sdcard:
            self._update(state=Messages.GoProStatus.State.MISSING_CARD)  # GoproNoSdcard
        elif not state['card'] and self.has_sdcard:
            self._update(state=Messages.GoProStatus.State.CONNECTED)  # GoproSdcardInserted
        state['card'] = self.has_sdcard

    def __handle_recording(self, previous_state):
        with self.__gc_lock:
            gc_data = self.__gc
            if gc_data is not None:
                # check if one team is 'invisible'
                both_teams_valid = all([t.teamNumber > 0 for t in gc_data.team]) or self.__rec_invisible

                # handle output
                if not self.__quiet:
                    output = "%s | %s | game state: %s | %s" % (
                        self.mode, "RECORDING!" if self.is_recording else "Not recording", gc_data.getGameState(), gc_data.secsRemaining)
                    print(output, flush=True)

                # handle game state changes
                if not self.__ignore and gc_data.secsRemaining < -self.__max_time:
                    # only stop, if we're still recording
                    if self.is_recording:
                        self.stopRecording()
                elif gc_data.gameState == GameControlData.STATE_SET and previous_state['time'] + self.__max_time < time.monotonic():
                    # too long in the set state, stop recording!
                    if self.is_recording:
                        self._logger.debug("Stopped recording because we were too long in set")
                        self.stopRecording()
                elif self.has_sdcard and not self.is_recording and both_teams_valid and (gc_data.gameState in self.__recording_states):
                    self.startRecording()
                elif self.is_recording and not (gc_data.gameState in self.__recording_states):
                    self.stopRecording()

                # handle game changes
                if previous_state['game'] != gc_data.gameState:
                    self._logger.debug("Changed game state from %s to %s @ %d", previous_state['game'], gc_data.gameState, time.time())
                    previous_state['time'] = time.monotonic()

                previous_state['game'] = gc_data.gameState
            else:
                if self.is_recording:
                    self.stopRecording()
                # no valid GC data, reset state back to initial
                previous_state['game'] = GameControlData.STATE_INITIAL

    def setUserSettings(self, settings: dict):
        # check the settings first
        for s, v in settings.items():
            if s not in self.__settings(GoPro.Settings):
                raise Exception('Unknown GoPro setting: ' + s)
            if v not in self.__settings(s):
                raise Exception('Invalid GoPro setting: ' + s + ' = ' + v)
            self.__user_settings[s] = v
        # apply settings, if connected
        if self.is_connected:
            self.__update_user_settings()

    def __settings(self, setting_type):
        return [val for var, val in vars(setting_type).items() if not var.startswith("_")]

    def __update_user_settings(self):
        self._logger.debug("Set user video settings")

        if self.__user_settings[GoPro.Settings.Resolution] != self.res:
            if not self._set_res(self.__user_settings[GoPro.Settings.Resolution]):
                self._logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.Resolution.__name__ + "'")
                self.__user_settings[GoPro.Settings.Resolution] = GoPro.Settings.Resolution.R_1080P

        if self.__user_settings[GoPro.Settings.FrameRate] != self.fps:
            if not self._set_fps(self.__user_settings[GoPro.Settings.FrameRate]):
                self._logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.FrameRate.__name__ + "'")
                self.__user_settings[GoPro.Settings.FrameRate] = GoPro.Settings.FrameRate.FR_30

        if self.__user_settings[GoPro.Settings.Fov] != self.fov:
            if not self._set_fov(self.__user_settings[GoPro.Settings.Fov]):
                self._logger.warning("The following setting can not be set for this cam: '" + GoPro.Settings.Fov.__name__ + "'")
                self.__user_settings[GoPro.Settings.Fov] = GoPro.Settings.Fov.SV

    @abstractmethod
    def _connect(self) -> bool:
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
    def _keep_alive(self):
        """
        Sends a keep alive signal to GoPro.
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
    def _last_video(self) -> Union[str, None]:
        """
        Returns the last recorded video or None, if there are no recordings.
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
