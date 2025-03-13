import zmq
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2, Preview
import time

from services.picam import PiCam
from utils.Configuration import Configuration


def main(ctx: zmq.Context = None, config: Configuration = None, cli: bool = False):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    _picam = PiCam.PiCam(
        _ctx, 
        _config.bus.port_send,
        _config.bus.port_recv,
        _config.gopro.quiet,
        _config.gopro.max_time,
        _config.gopro.rec_invisible,
        logger=_config.logger())

    _picam.run()

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main(cli=True)
