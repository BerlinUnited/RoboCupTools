import threading
import logging
import zmq
import time
import datetime                                                                             
from picamera2.encoders import H264Encoder, Quality
from picamera2 import Picamera2, Preview

import traceback
from typing import Union
from abc import ABCMeta, abstractmethod
from services import Messages
from services.data.GameControlData import GameControlData

class PiCam(threading.Thread, metaclass=ABCMeta):
    def __init__(self, 
                context: zmq.Context,
                mq_send: int,
                mq_recv: int,
                quiet: bool,
                max_time: int,
                rec_invisible: bool = False,
                logger: logging.Logger = None):
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)
        self.__rec_invisible = rec_invisible
        self.__quiet = quiet
        self.__max_time = max_time
        self.__update_interval = 0.5  # in seconds

        self.__pub: zmq.Socket = context.socket(zmq.PUB)
        self.__pub.connect(f"tcp://localhost:{mq_send}")

        self.__sub: zmq.Socket = context.socket(zmq.SUB)
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GameController.key)
        self.__sub.connect(f"tcp://localhost:{mq_recv}")

        self._cancel = threading.Event()

        self.__gc = None
        self.__gc_recv = threading.Thread(target=self.__handle_gc)
        self.__gc_lock = threading.Lock()

        self.__recording_states = [
            GameControlData.STATE_STANDBY,
            GameControlData.STATE_READY,
            GameControlData.STATE_SET,
            GameControlData.STATE_PLAYING
        ]
        self._is_recording = False

        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(raw={"size":(1640,1232)},main={"size": (1640, 1232)}))
        self.picam2.start_preview(Preview.NULL)
        self.encoder = H264Encoder()
    
    #@property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def is_canceled(self) -> bool:
        return self._cancel.is_set()

    def startRecording(self):
        if not self.is_recording():
            self._is_recording = True
            output_name = "/home/pi/recording-{date:%Y-%m-%d_%H:%M:%S}.h264".format( date=datetime.datetime.now())
            timestamp_name = "/home/pi/timestamp-{date:%Y-%m-%d_%H:%M:%S}.txt".format( date=datetime.datetime.now())
            self.picam2.start_recording(self.encoder, output_name, quality=Quality.MEDIUM, pts=timestamp_name)

    def stopRecording(self):
        if self.is_recording():
            self._is_recording = False
            self.picam2.stop_recording()

    def cancel(self):
        self._cancel.set()

    def run(self):
        # init game state
        previous_state = {'game': GameControlData.STATE_INITIAL, 'time': time.monotonic(), 'card': True}
        self.__gc_recv.start()
        # run until canceled
        while not self.is_canceled:
            try:
                # handling recording state
                self.__handle_recording(previous_state)
                #self.__keep_alive()
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
        self._logger.debug("PiCam thread finished.")


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

    def __handle_recording(self, previous_state):
        with self.__gc_lock:
            gc_data = self.__gc
            if gc_data is not None:
                # check if one team is 'invisible'
                both_teams_valid = all([t.teamNumber > 0 for t in gc_data.team]) or self.__rec_invisible
                is_berlin_united_playing = any(t.teamNumber == 4 for t in gc_data.team)
                # handle output
                if not self.__quiet:
                    #output = f"| {"RECORDING!" if self.is_recording else "Not recording"} | game state: {gc_data.getGameState()} | {gc_data.secsRemaining}"
                    output = f"| game state: {gc_data.getGameState()} | recording: {self.is_recording()} | {gc_data.secsRemaining}"
                    print(output, flush=True)

                # handle game state changes
                #if not self.__ignore and gc_data.secsRemaining < -self.__max_time:
                if gc_data.secsRemaining < -self.__max_time:
                    # only stop, if we're still recording
                    #if self.is_recording:
                    self.stopRecording()
                elif gc_data.gameState == GameControlData.STATE_SET and previous_state['time'] + self.__max_time < time.monotonic():
                    # too long in the set state, stop recording!
                    #if self.is_recording:
                    self._logger.debug("Stopped recording because we were too long in set")
                    self.stopRecording()
                #elif not self.is_recording and both_teams_valid and (gc_data.gameState in self.__recording_states):
                elif (both_teams_valid or is_berlin_united_playing) and (gc_data.gameState in self.__recording_states):
                    self.startRecording()
                #elif self.is_recording and not (gc_data.gameState in self.__recording_states):
                elif not (gc_data.gameState in self.__recording_states):
                    self.stopRecording()

                # handle game changes
                if previous_state['game'] != gc_data.gameState:
                    self._logger.debug("Changed game state from %s to %s @ %d", previous_state['game'], gc_data.gameState, time.time())
                    previous_state['time'] = time.monotonic()

                previous_state['game'] = gc_data.gameState
            else:
                #if self.is_recording:
                self.stopRecording()
                # no valid GC data, reset state back to initial
                previous_state['game'] = GameControlData.STATE_INITIAL

    #@abstractmethod
    #def _is_recording(self) -> bool:
    #    """
    #    Indicates, whether the GoPro is recording (True) or not (False).
    #    :return:
    #    """
    #    return False