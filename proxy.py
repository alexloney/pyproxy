#!python

import requests
import os
import sys
import io
import gzip
from bs4 import BeautifulSoup
from http.server import BaseHTTPRequestHandler, HTTPServer

target = ''
hostname = 'localhost'
port = 9000

override_headers = {
        # 'cookie': '',
        # 'host': '',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
}

class MyServer(BaseHTTPRequestHandler):
    def gzipencode(self, content):
        out = io.BytesIO()
        f = gzip.GzipFile(fileobj=out, mode='w', compresslevel=5)
        f.write(content)
        f.close()
        return out.getvalue()

    def do_GET(self):
        print('='*80)
        print('Request Headers')
        print('='*80)
        print(self.headers)
        print('-'*80 + '\n')
        
        newpath = target + self.path

        print('='*80)
        print('New Path')
        print('='*80)
        print(newpath)
        print('-'*80 + '\n')

        for header in override_headers:
            # Before overriding, delete the existing header, HTTP headers are case-insensitive
            # so we will loop through and delete the matching headers.
            for headername in self.headers:
                if headername.lower() == header.lower():
                    del self.headers[headername]

            # Now append the new header
            self.headers[header] = override_headers[header]

        print('='*80)
        print('Updated Headers')
        print('='*80)
        print(self.headers)
        print('-'*80 + '\n')

        r = requests.get(newpath, headers = self.headers)
        
        print('='*80)
        print('Response Headers')
        print('='*80)
        print('Status Code: ' + str(r.status_code))
        for header in r.headers:
            print(header + ': ' + r.headers[header])
        print('-'*80 + '\n')

        self.send_response(r.status_code)
        for item in r.headers:
            self.send_header(item, r.headers[item])
        self.end_headers()

        self.wfile.write(bytes(r.text, 'utf-8'))

        # NOTE: If gzip encoding, we can do the following
        # self.wfile.write(self.gzipencode(bytes(r.text, 'utf-8')))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: ' + sys.argv[0] + ' <target> <port>')
        sys.exit(1)

    target = sys.argv[1]
    port = int(sys.argv[2])

    webServer = HTTPServer((hostname, port), MyServer)
    print('Server started http://' + hostname + ':' + str(port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Server stopped.')
