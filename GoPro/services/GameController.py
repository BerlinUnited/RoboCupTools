import struct
import threading
import socket
import logging
import time

import zmq
import zmq.asyncio

from services.data.GameControlData import GameControlData
from services.Messages import Message, GameControllerMessage, GameControllerDisconnect, GameControllerInvalidSource, \
    GameControllerShutdown
from utils.Configuration import Configuration


class GameController(threading.Thread):
    """
    The GameController class is used to receive the infos of a game.
    If new data was received, it gets parsed and published on the blackboard.
    """

    def __init__(self,
                 context: zmq.Context,
                 mq_port: int,
                 source: str = None,
                 port: int = 3838,
                 true_data: bool = True,
                 true_data_port: int = 3636,
                 logger: logging.Logger = None):
        """
        Constructor.
        Init class variables and establish the udp socket connection to the GameController.
        """
        super().__init__()

        self.__cancel = threading.Event()

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__socket.bind(('', port))
        self.__socket.settimeout(1)  # in sec

        self.__true_data = true_data
        self.__true_data_port = true_data_port
        self.__true_data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__true_data_timestamp = 0
        self.__true_data_timeout = 1  # in sec

        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)
        self.__source = str(source) if source is not None else None
        self.__port = port

        self.__pub = context.socket(zmq.PUB)  # type: zmq.Socket
        self.__pub.connect(f"tcp://localhost:{mq_port}")

    def run(self):
        """
        Main method of this thread.
        It listens on the socket for incoming GameController messages, parses them and publishes it on the blackboard.

        :return: nothing
        """
        self.__logger.info("Listen to GameController %s", '' if self.__source is None else self.__source)
        while not self.__cancel.is_set():
            try:
                try:
                    # receive GC data
                    data, address = self.__socket.recvfrom(8192)
                    # only if we received something, parse & publish message
                    if len(data) > 0:
                        if self.__source is None or address[0] == self.__source:
                            message = GameControlData(data)
                            # only publish, if we've got the 'correct' data (False = False & True = True)
                            if self.__true_data == message.isTrueData():
                                # NOTE: we're still receiving the 'normal' data, even if we've also requested the
                                #       TrueData additionally!
                                self.__true_data_timestamp = time.time()
                                self.__publish(GameControllerMessage(message))

                            if self.__true_data and time.time() > self.__true_data_timestamp + self.__true_data_timeout:
                                self.__request_true_data(address[0])
                        else:
                            self.__publish(GameControllerInvalidSource(address[0].encode()))
                            self.__logger.debug("Got data from a invalid source: %s != %s", address[0], self.__source)

                except socket.timeout:
                    self.__publish(GameControllerDisconnect())
                    self.__logger.warning("Not connected to GameController?")
                    continue
                except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                    raise  # this is handled by the outer try/catch
                except Exception as ex:
                    # Unknown exception
                    self.__logger.error("Unknown exception: " + str(ex))
                    continue
            except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                self.stop()

        try:
            # try to publish shutdown message; ignore, in case the context is already terminated
            self.__publish(GameControllerShutdown())
        except zmq.ContextTerminated:
            pass

        self.__socket.close()
        self.__true_data_socket.close()
        self.__pub.close()
        self.__logger.info("GameController thread finished.")

    def __request_true_data(self, address):
        self.__logger.debug("Request true data from GameController")
        request = struct.pack('4sB',
                              GameControlData.GAMECONTROLLER_TRUE_DATA_REQUEST,
                              GameControlData.GAMECONTROLLER_TRUE_DATA_VERSION)
        self.__true_data_socket.sendto(request, (address, self.__true_data_port))

    def __publish(self, message: Message):
        if not self.__pub.closed:
            self.__pub.send_multipart([message.key, message.value])

    def wait(self, timeout=None):
        self.__cancel.wait(timeout)

    def stop(self):
        """
        Stops this GameController thread.

        :return: nothing
        """
        self.__cancel.set()
        self.__socket.settimeout(0)
        # send dummy in order to 'interrupt' receiving socket
        self.__socket.sendto(b'', ('', self.__port))

    def setSource(self, source):
        """
        Sets the source ip address of the GameController, others are ignored.
        :param source: the new source ip address
        :return: nothing
        """
        self.__source = str(source) if source is not None else None


def main(ctx: zmq.Context = None, config: Configuration = None):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    _gameController = GameController(_ctx,
                                     _config.bus.port_send,
                                     source=_config.gc.source,
                                     true_data=_config.gc.true_data,
                                     true_data_port=_config.gc.true_data_port,
                                     logger=_config.logger())
    try:
        _gameController.run()
    except (KeyboardInterrupt, SystemExit):
        pass

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main()
