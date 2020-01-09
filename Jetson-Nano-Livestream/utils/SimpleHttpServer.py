import socket, re, urllib.parse, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from utils import Event

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if None != re.search("/set", self.path):
            n = urllib.parse.urlparse(self.path)
            x = urllib.parse.parse_qs(n.query)

            Event.fire(Event.SettingsMessage(x))

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            output = str(x)
            self.wfile.write(output.encode('utf-8'))
            return
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            output = "404 requested endpoint not available"
            self.wfile.write(output.encode('utf-8'))
            return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        try:
            self.socket.close()
            HTTPServer.shutdown(self)
        except:
            pass

class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join(timeout=5)

    def stop(self):
        self.server.shutdown()
        self.waitForThread()
