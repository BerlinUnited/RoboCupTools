import zmq

from services.gopro import GoPro, GoProCam, OpenGoPro
from utils.Configuration import Configuration


def main(ctx: zmq.Context = None, config: Configuration = None, cli: bool = False):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    if _config.gopro.ssid is not None:
        _gopro: GoPro.GoPro = GoProCam.GoProCam(_ctx,
                                                _config.bus.port_send,
                                                _config.bus.port_recv,
                                                _config.gopro.device,
                                                _config.gopro.ssid,
                                                _config.gopro.passwd,
                                                _config.gopro.ble_mac,
                                                _config.gopro.quiet,
                                                _config.gopro.ignore,
                                                _config.gopro.max_time,
                                                _config.gopro.rec_invisible,
                                                logger=_config.logger())
    else:
        _gopro: GoPro.GoPro = OpenGoPro.OpenGoPro(_ctx,
                                                  _config.bus.port_send,
                                                  _config.bus.port_recv,
                                                  _config.gopro.quiet,
                                                  _config.gopro.ignore,
                                                  _config.gopro.max_time,
                                                  _config.gopro.rec_invisible,
                                                  logger=_config.logger())

    if cli:
        _gopro.start()
        try:
            while True:
                cmd = input('>>>')
                if cmd in ['h', 'help']:
                    print('start|stop|status|photo|mode|exit')
                elif cmd == 'start':
                    _gopro.startRecording()
                elif cmd == 'stop':
                    _gopro.stopRecording()
                elif cmd == 'status':
                    print(_gopro.state)
                elif cmd == 'photo':
                    _gopro.take_photo()
                elif cmd == 'mode':
                    print(_gopro.mode)
                elif cmd in ['e', 'exit']:
                    break
        except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
            pass
        _gopro.cancel()
        _gopro.join()
    else:
        _gopro.run()

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main(cli=True)
