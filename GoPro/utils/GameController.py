import threading, socket, struct, datetime, time

from utils import Logger, blackboard
from utils.GameControlData import GameControlData

GAME_CONTROLLER_PORT = 3838

TRUEDATAREQUEST_HEADER = 'RGTr'
TRUEDATAREQUEST_VERSION = 0
TRUEDATAREQUEST_PORT = 3636
REQUEST_TRUE_DATA_AFTER = 1

# setup logger for network related logs
logger = Logger.getLogger("GameController")

class GameController(threading.Thread):
    """
    The GameController class is used to receive the infos of a game.
    If new data was received, it gets parsed and published on the blackboard.
    """

    def __init__(self, source=None, tryToGetTrueData=True):
        """
        Constructor.
        Inits class variables and establish the udp socket connection to the GameController.
        """
        super().__init__()

        self.tryToGetTrueData = tryToGetTrueData
        self.__cancel = threading.Event()

        self.timestampOfLastTrueGameControlData = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.bind(('', GAME_CONTROLLER_PORT))
        self.socket.settimeout(5)  # in sec

        self.__source = str(source) if source is not None else None
        
    def requestTrueData(self, gameControllerAddress):
        request = struct.pack('4sB', bytes(TRUEDATAREQUEST_HEADER, 'UTF-8'), TRUEDATAREQUEST_VERSION)
        self.trueDataSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.trueDataSocket.sendto(request, (gameControllerAddress, TRUEDATAREQUEST_PORT))
        self.trueDataSocket.close()
        pass

    def run(self):
        """
        Main method of this thread.
        It listens on the socket for incoming GameController messages, parses them and publishes it on the blackboard.

        :return: nothing
        """
        logger.info("Listen to GameController %s", '' if self.__source is None else self.__source)
        while not self.__cancel.is_set():
            try:
                # receive GC data
                data, address = self.socket.recvfrom(8192)
                # only if we recieved somethind, parse & publish message
                if len(data) > 0 and (self.__source is None or address[0] == self.__source):
                    message = GameControlData(data)

                    # accept the message if it is true data
                    if self.tryToGetTrueData == message.isTrueData or (self.tryToGetTrueData and time.time() - self.timestampOfLastTrueGameControlData > 2 * REQUEST_TRUE_DATA_AFTER):
                        #print("message.isTrueData: " + str(message.isTrueData))
                        blackboard['gamecontroller'] = message

                    if self.tryToGetTrueData:
                        if message.isTrueData:
                            self.timestampOfLastTrueGameControlData = time.time()
                        elif time.time() - self.timestampOfLastTrueGameControlData >= REQUEST_TRUE_DATA_AFTER:
                            print("requestTrueData: " + str(address[0]))
                            self.requestTrueData(address[0])
                else:
                    logger.debug("Got data from a invalid source: %s != %s", address[0], self.__source)

            except socket.timeout:
                blackboard['gamecontroller'] = None
                logger.warning("Not connected to GameController?")
                self.message = None
                continue
            except Exception as ex:
                # Unknown exception
                self.message = None
                logger.error("Unknown exception: " + str(ex))
                continue

        self.socket.close()
        logger.debug("GameController thread finished.")

    def cancel(self):
        """
        Cancels this GameController thread.

        :return: nothing
        """
        self.__cancel.set()
        self.socket.settimeout(0)
        # send dummy in order to 'interrupt' receiving socket
        self.socket.sendto(b'', ('', GAME_CONTROLLER_PORT))

    def setSource(self, source):
        """
        Sets the source ip address of the GameController, others are ignored.
        :param source: the new source ip address
        :return: nothing
        """
        self.__source = str(source) if source is not None else None