#!/usr/bin/env python3
# -*- coding: utf8 -*-
import logging
import threading
import zmq
import zmq.error

from utils.Configuration import Configuration


class MessageBusMonitor(threading.Thread):
    def __init__(self, context: zmq.Context, logger: logging.Logger = None):
        super().__init__()

        self.__in: zmq.Socket = context.socket(zmq.PAIR)
        self.__out: zmq.Socket = context.socket(zmq.PAIR)

        self.__in.linger = self.__out.linger = 0
        self.__in.hwm = self.__out.hwm = 1

        iface = "inproc://zmq_monitoring"
        self.__in.bind(iface)
        self.__out.connect(iface)

        self.__cancel = threading.Event()
        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)

    def stop(self):
        self.__cancel.set()
        if not self.__in.closed:
            self.__in.send(b'EXIT')  # HACK: to interrupt recv()

    @property
    def input(self):
        return self.__in

    def run(self) -> None:
        self.__logger.info('Start monitoring thread')
        while not self.__cancel.is_set():
            try:
                data = self.__out.recv_multipart()
                if data[0][:1] == b'\x01':
                    self.__logger.debug(f'Consumer registered to "{data[0][1:].decode()}" ...')
                elif data[0][:1] == b'\x00':
                    self.__logger.debug(f'Consumer unregistered from "{data[0][1:].decode()}" ...')
                else:
                    self.__logger.debug(data)
            except zmq.error.ContextTerminated:
                self.__cancel.set()
            except Exception as ex:
                self.__logger.error(ex)

        self.__in.close()
        self.__out.close()
        self.__logger.info('Monitoring thread finished')


class MessageBus(threading.Thread):
    def __init__(self, context: zmq.Context, port_send: int, port_recv: int, monitor: MessageBusMonitor = None, logger: logging.Logger = None):
        super().__init__()
        self.__cancel = threading.Event()
        self.__ctx = context
        self.__port_send = port_send
        self.__port_recv = port_recv
        self.__monitor = monitor
        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)

    def wait(self, timeout=None):
        self.__cancel.wait(timeout)

    def stop(self):
        self.__cancel.set()

    def run(self) -> None:
        self.__logger.info(f'Create producer socket (port = {self.__port_recv}) ...')
        # Socket facing producers
        frontend = self.__ctx.socket(zmq.XPUB)
        frontend.bind(f"tcp://*:{self.__port_recv}")

        self.__logger.info(f'Create consumer socket (port = {self.__port_send}) ...')
        # Socket facing consumers
        backend = self.__ctx.socket(zmq.XSUB)
        backend.bind(f"tcp://*:{self.__port_send}")

        try:
            self.__logger.info('Start proxy ...')
            zmq.proxy(frontend, backend, self.__monitor.input if self.__monitor else None)
        except zmq.error.ContextTerminated:
            pass  # ignore, since we expected it on stop()
        finally:
            frontend.close()
            backend.close()
        self.__logger.info('Messagebus finished')


def main(ctx: zmq.Context = None, config: Configuration = None):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    _monitor = MessageBusMonitor(_ctx, logger=_config.logger()) if _config.bus.monitor else None
    _bus = MessageBus(_ctx, _config.bus.port_send, _config.bus.port_recv, _monitor, logger=_config.logger())

    if _monitor:
        _monitor.start()

    try:
        _bus.run()
    except (KeyboardInterrupt, SystemExit):
        pass

    if _monitor:
        _monitor.stop()
        _monitor.join()

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main()
