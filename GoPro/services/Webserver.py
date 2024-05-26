import json
import logging
import os
import threading
from http.server import HTTPServer as SimpleHTTPServer, SimpleHTTPRequestHandler

import websockets
import websockets.sync.server
import zmq

from services import Messages
from services.data.GameControlData import GameControlData
from utils.Configuration import Configuration


class HTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), './web/'), **kwargs)

    def log_message(self, format, *args):
        message = format % args
        logging.debug("%s - %s - %s" % (self.address_string(), self.log_date_time_string(), message))

    def do_GET(self):
        if self.path == '/websocket':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str(self.server.websocket).encode('utf-8') if self.server.websocket else b'')
        else:
            super().do_GET()


class HTTPServer(SimpleHTTPServer):
    def __init__(self, server_address, ws_port: int = None):
        super().__init__(server_address, HTTPHandler)
        self.__ws_port = ws_port

    @property
    def websocket(self) -> int:
        return self.__ws_port


class Webserver(threading.Thread):

    def __init__(self, context: zmq.Context, mq_port: int, http_port: int, ws_port: int, logger: logging.Logger = None):
        super().__init__()

        self.__http_port = http_port
        self.__ws_port = ws_port

        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)
        self.__cancel = threading.Event()

        self.__sub: zmq.Socket = context.socket(zmq.SUB)
        self.__sub.setsockopt(zmq.SUBSCRIBE, b'')  # subscribe to everything
        self.__sub.connect(f"tcp://localhost:{mq_port}")

        self.__ws_clients = set()
        self.__ws_clients_lock = threading.Lock()
        self.__ws_logger = self.__logger.getChild('websocket')
        self.__ws_logger.setLevel(logging.WARNING)

    def wait(self, timeout=None):
        self.__cancel.wait(timeout)

    def stop(self):
        self.__cancel.set()

    def run(self):
        self.__logger.info('Start Webserver')

        wsd = websockets.sync.server.serve(self.__handler, "", self.__ws_port, logger=self.__ws_logger)
        threading.Thread(target=wsd.serve_forever).start()

        httpd = HTTPServer(("", self.__http_port), ws_port=self.__ws_port)
        threading.Thread(target=httpd.serve_forever).start()

        poller = zmq.Poller()
        poller.register(self.__sub, zmq.POLLIN)

        data = {}  # storing all received data
        while not self.__cancel.is_set():
            try:
                # Poll for events, timeout set to 500 milliseconds (0.5 second)
                if poller.poll(500):
                    topic, message = self.__sub.recv_multipart()  # type: bytes, bytes

                    source, kind = topic.decode().split('/')
                    if topic == Messages.GameControllerMessage.key:
                        data[source] = str(GameControlData(message))
                    else:
                        data[source] = message.decode() if len(message) > 0 else kind

                    with self.__ws_clients_lock:
                        ws_message = json.dumps(data)
                        for client in self.__ws_clients:
                            client.send(ws_message)
            except (KeyboardInterrupt, SystemExit, zmq.error.ContextTerminated):
                self.stop()

        wsd.shutdown()
        with self.__ws_clients_lock:
            for client in self.__ws_clients:
                client.close()
        httpd.shutdown()
        self.__sub.close()
        self.__logger.info('Stopped Webserver')

    def __handler(self, websocket):
        # Add the new client to our set
        with self.__ws_clients_lock:
            self.__ws_clients.add(websocket)
        try:
            while True:
                message = websocket.recv()
                if message is None:
                    break
        except websockets.exceptions.ConnectionClosedOK:
            pass
        except Exception as e:
            print(f"Connection error ({type(e)}): {e}")
        finally:
            # Remove the client on disconnect
            with self.__ws_clients_lock:
                self.__ws_clients.remove(websocket)


def main(ctx: zmq.Context = None, config: Configuration = None):
    _ctx = ctx if ctx else zmq.Context.instance()
    _config = config if config else Configuration()

    _server = Webserver(_ctx, _config.bus.port_recv, _config.web.http_port, _config.web.ws_port, logger=_config.logger())

    try:
        _server.run()
    except (KeyboardInterrupt, SystemExit):
        _server.stop()

    if not ctx:
        _ctx.term()


if __name__ == '__main__':
    main()
