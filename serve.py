#!/usr/bin/env python3

import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) >= 2 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg': 'image/svg+xml',
        '.css': 'text/css',
        '.js':  'application/x-javascript',
        '.wasm':  'application/wasm',
        '': 'application/octet-stream',
    }

    def __init__(self, *args, **kwargs):
        print('init handler')
        super().__init__(*args, **kwargs)


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
