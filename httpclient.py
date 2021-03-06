#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Maharsh Patel, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def parse_url(self, url):
        # https://docs.python.org/2/library/urlparse.html
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc

        path = parsed_url.path
        if not path:
            path = "/"
        
        port = 80
        if parsed_url.port:
            port = parsed_url.port
        
        return (host, path, port)

    def parse_response(self, response):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        response_code = int(response.split("\r\n")[0].split(" ")[1])    # right after HTTP/1.1
        body = response.split("\r\n\r\n")[1]   # everything after headers

        return (response_code, body)

    def get_headers(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, path, port = self.parse_url(url)
        
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        request = "GET {} HTTP/1.1\r\n".format(path)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Connection: close\r\n\r\n"

        self.connect(host.split(":")[0], port)
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()

        code, body = self.parse_response(response)

        print(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, path, port = self.parse_url(url)

        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
        content = ""
        content_length = 0
        if args:
            content = urllib.parse.urlencode(args)
            # Kris, https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes
            content_length = len(content.encode("utf-8"))
        
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
        request = "POST {} HTTP/1.1\r\n".format(path)
        request += "Host: {}\r\n".format(host)
        request += "Accept: */*\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: {}\r\n".format(content_length)
        request += "Connection: close\r\n\r\n"

        if content: 
            request += content

        self.connect(host.split(":")[0], port)
        self.sendall(request)

        response = self.recvall(self.socket)
        self.close()

        code, body = self.parse_response(response)

        print(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
