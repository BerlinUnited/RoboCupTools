import json
from enum import Enum

from services.data.GameControlData import GameControlData


class Message:
    __key = b''
    __value = b''

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: bytes):
        self.__value = value


class GameController(Message):
    key = b'gc/'


class GameControllerMessage(GameController):
    key = b'gc/message'

    def __init__(self, value):
        if isinstance(value, bytes):
            self.value = value
        elif isinstance(value, GameControlData):
            self.value = value.pack()
        else:
            raise Exception('Invalid type for GameControllerMessage')


class GameControllerInvalidSource(GameController):
    key = b'gc/invalid_source'

    def __init__(self, value: bytes):
        self.value = value


class GameControllerDisconnect(GameController):
    key = b'gc/disconnect'


class GameControllerShutdown(GameController):
    key = b'gc/shutdown'


class GoPro(Message):
    key = b'gopro/'


class GoProStatus(GoPro):
    key = b'gopro/status'

    class State(Enum):
        DISCONNECTED = 0
        CONNECTING = 1
        CONNECTED = 2
        MISSING_CARD = 3
        RECORDING = 4

    def __init__(self, value: dict):
        self.value = json.dumps(value).encode()

class GoProShutdown(GoPro):
    key = b'gopro/shutdown'
