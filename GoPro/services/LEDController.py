import logging
import threading
import time
import json

import zmq
from typing_extensions import Self

from services import Messages
from services.data.GameControlData import GameControlData
from utils.Configuration import Configuration

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    class _GPIOMock:
        """Mock class in case this is not running on a raspi."""

        class Dummy:
            def __call__(self, *args, **kwargs):
                pass

        def __getattribute__(self, item):
            return _GPIOMock.Dummy()


    # Create an instance alias
    GPIO = _GPIOMock()


class LED:
    """
    Represent a LED

    Setting a new state (on/off) doesn't immediately take effect. The new state is only applied if `update()` is
    called. In order to immediately update the state, use the `update` parameter on the respective method.
    This implementation somewhat follows the builder pattern.
    """

    def __init__(self, pin: int):
        self.__pin = pin
        self.__state = False

        GPIO.setup(self.__pin, GPIO.OUT)
        self.update()

    @property
    def pin(self) -> int:
        return self.__pin

    def on(self, update: bool = False):
        self.__state = True
        if update:
            self.update()

    def off(self, update: bool = False):
        self.__state = False
        if update:
            self.update()

    def toggle(self, update: bool = False):
        self.__state = not self.__state
        if update:
            self.update()

    def update(self):
        if self.__state:
            GPIO.output(self.__pin, GPIO.HIGH)
        else:
            GPIO.output(self.__pin, GPIO.LOW)


class LEDState:
    ON = 'ON'
    OFF = 'OFF'
    BLINK = 'BLINK'

    def __init__(self, led: LED):
        self.__led = led
        self.__blink_time = time.time()
        self.__state = LEDState.OFF
        self.__delay = 0.0
        self.__valid = 0.0
        self.__lock = threading.RLock()

    def reset(self) -> Self:
        with self.__lock:
            self.__state = LEDState.OFF
            self.__delay = 0.0
            self.__valid = 0.0
        return self

    def on(self, valid: float = 0.0) -> Self:
        with self.__lock:
            self.reset()
            self.__state = LEDState.ON
            self.__valid = time.time() + valid if valid > 0 else 0.0
        return self

    def off(self) -> Self:
        with self.__lock:
            self.reset()
            self.__state = LEDState.OFF
        return self

    def blink(self, delay: float = 1.0, valid: float = 0.0) -> Self:
        with self.__lock:
            self.reset()
            self.__state = LEDState.BLINK
            self.__delay = delay
            self.__valid = time.time() + valid if valid > 0 else 0.0
        return self

    def update(self):
        with self.__lock:
            if self.__state == LEDState.ON:
                self.__led.on()
            elif self.__state == LEDState.OFF:
                self.__led.off()
            elif self.__state == LEDState.BLINK:
                if self.__delay > 0 and time.time() > self.__blink_time + self.__delay:
                    self.__led.toggle()
                    self.__blink_time = time.time()
            # if state validity is expired, set LED off
            if self.__valid > 0 and time.time() > self.__valid:
                self.__led.off()
            # apply LED state
            self.__led.update()


class LEDController(threading.Thread):
    def __init__(self):
        super().__init__()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.red = LEDState(LED(22))
        self.blue = LEDState(LED(17))
        self.green = LEDState(LED(27))

        self.__leds = [self.red, self.blue, self.green]
        self.__cancel = threading.Event()

    def on(self):
        for led in self.__leds:
            led.on().update()

    def off(self):
        for led in self.__leds:
            led.off().update()

    def update(self):
        for led in self.__leds:
            led.update()

    def start_animation(self):
        for i in range(0, 3):
            self.on()
            time.sleep(0.2)
            self.off()
            time.sleep(0.2)

    def run(self):
        self.start_animation()
        while not self.__cancel.is_set():
            time.sleep(0.1)
            self.update()
        self.off()

    def stop(self):
        self.__cancel.set()
        self.off()


class LEDServer(threading.Thread):

    def __init__(self, context: zmq.Context, mq_port: int, server: LEDController, logger: logging.Logger = None):
        super().__init__()

        self.__server = server
        self.__logger = logging.getLogger('LED') if logger is None else logger.getChild('LED')
        self.__cancel = threading.Event()

        self.__sub = context.socket(zmq.SUB)  # type: zmq.Socket
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GoPro.key)
        self.__sub.setsockopt(zmq.SUBSCRIBE, Messages.GameController.key)
        self.__sub.connect(f"tcp://localhost:{mq_port}")

        self.gopro = None  # type: dict|None
        self.gc = None  # type: GameControlData|None

    def wait(self, timeout=None):
        self.__cancel.wait(timeout)

    def stop(self):
        self.__cancel.set()

    def run(self):
        self.__logger.info('Start LED controller')
        poller = zmq.Poller()
        poller.register(self.__sub, zmq.POLLIN)
        while not self.__cancel.is_set():
            try:
                # Poll for events, timeout set to 500 milliseconds (0.5 second)
                if poller.poll(500):
                    topic, message = self.__sub.recv_multipart()  # type: bytes, bytes
                    self.__handle_message(topic, message)
                # always update the LED states
                self.__handle_leds()
            except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                self.stop()
        self.__sub.close()
        self.__logger.info('Stopped LED controller')

    def __handle_message(self, topic, message):
        if topic == Messages.GoProStatus.key:
            self.gopro = json.loads(message)
        elif topic == Messages.GoProShutdown.key:
            self.gopro = None
        elif topic == Messages.GameControllerMessage.key:
            self.gc = GameControlData(message)
        elif topic == Messages.GameControllerInvalidSource.key:
            self.gc = 'invalid'
        elif topic == Messages.GameControllerShutdown.key or topic == Messages.GameControllerDisconnect.key:
            self.gc = None
        else:
            self.__logger.warning(f'Unknown topic: topic')

    def __handle_leds(self):
        self.__handle_led_blue()
        self.__handle_led_green()
        self.__handle_led_red()

    def __handle_led_blue(self):
        if self.gopro is None or self.gopro['state'] == Messages.GoProStatus.State.DISCONNECTED.value:
            self.__server.blue.blink(0.4, 1)  # gopro (network) not available/visible (disconnected)
        elif self.gopro['state'] == Messages.GoProStatus.State.CONNECTING.value:
            self.__server.blue.blink(0.8, 1)  # connecting to gopro (network)
        elif self.gopro['state'] == Messages.GoProStatus.State.CONNECTED.value:
            self.__server.blue.on(valid=1)  # is ready to record
        elif self.gopro['state'] == Messages.GoProStatus.State.MISSING_CARD.value:
            self.__server.blue.blink(valid=1)  # gopro has no sdcard
        elif self.gopro['state'] == Messages.GoProStatus.State.RECORDING.value:
            pass  # nothing to do for blue LED
        else:
            self.__server.blue.blink(0.2, 1)  # something else (unknown)

    def __handle_led_green(self):
        if self.gc is None:
            # nothing received from GameController
            self.__server.green.off()
        elif self.gc == 'invalid':
            self.__server.green.blink(0.4, valid=1)
        elif not all([t.teamNumber > 0 for t in self.gc.team]):
            # only one team in the game (the other is "INVISIBLE")
            self.__server.green.blink(valid=1)
        else:
            # GameController is ready
            self.__server.green.on(valid=1)

    def __handle_led_red(self):
        if self.gopro is not None and self.gopro['state'] == 4:
            # gopro is recording
            self.__server.red.blink(valid=1)
        elif self.gopro is not None and self.gopro['state'] == 3:
            # gopro has no sdcard!
            self.__server.red.blink(delay=0.1, valid=1)
        else:
            # gopro is NOT recording
            self.__server.red.off()


def main(ctx: zmq.Context = None, config: Configuration = None):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    _controller = LEDController()
    _server = LEDServer(_ctx, _config.bus.port_recv, _controller, logger=_config.logger())

    _controller.start()
    try:
        _server.run()
    except (KeyboardInterrupt, SystemExit) as e:
        pass

    _controller.stop()
    if not ctx:
        _ctx.term()
    _controller.join()


if __name__ == '__main__':
    main()
