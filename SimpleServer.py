#!/usr/bin/env python3
import os
import sys
import logging
import cgi
import json
import socketserver
from http.server import SimpleHTTPRequestHandler
from urllib import parse
from subprocess import Popen, PIPE, STDOUT

if 'PORT' in os.environ:
    PORT = int(os.environ['PORT'])
    print('Got port', PORT)
else:
    PORT = 8000


import openPitMining


class ServerHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.error(self.headers)
        super().do_GET()

    def do_POST(self):
        if self.path == '/openPitMining.py':
            ctype, pdict = cgi.parse_header(self.headers.get('content-type', ''))
            length = int(self.headers.get('content-length', 0))
            raw_body = self.rfile.read(length)

            jsdict = None

            # Primary: parse JSON directly when sent with application/json
            if ctype == 'application/json':
                try:
                    jsdict = json.loads(raw_body.decode('utf-8'))
                except Exception:
                    jsdict = None

            # Fallback: attempt to parse as urlencoded and extract JSON payload key
            if jsdict is None:
                try:
                    data = parse.parse_qs(raw_body.decode('utf-8'), keep_blank_values=1)
                    for val in data:
                        try:
                            jsdict = json.loads(val)
                            break
                        except Exception:
                            continue
                except Exception:
                    jsdict = None

            if jsdict is not None:
                jsdict = openPitMining.handleoptimize(jsdict)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(jsdict).encode('utf-8'))
                return
        else:
            super().do_GET()

Handler = ServerHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

print("Starting simple server")
print("serving at port", PORT)
httpd.serve_forever()
