# -*- coding: utf-8 -*-
"""
FileName:   app
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
from httpserver.exceptions import MethodNotAllowed
import json
from httpserver.response import HTTPResponse
from httpserver.router import Router
from httpserver.server import Server
try:
    from ujson import dumps as json_dumps
except ImportError:
    json_dumps = json.dumps


class Application(object):

    def __init__(self, url_handler_list):
        self.router = None
        self.server = None
        self.create_router(url_handler_list)

    def create_router(self, url_handler_list):
        if self.router:
            raise Exception("route has exist")

        self.router = Router()
        for uri, handler in url_handler_list:
            if not issubclass(handler, RequestHandler):
                raise Exception("handler type is error")

            self.router.add(uri, handler)

    def run(self, host, port, backlog=128):
        self.server = Server(self)
        self.server.run(host, port, backlog)

    def stop(self):
        self.server.stop()
        self.router = None


class RequestHandler(object):

    def __init__(self, request):
        self.request = request

    def execute_handler(self, *args, **kwargs):
        method = self.request.method
        if method == "HEAD":
            self.head(*args, **kwargs)
        elif method == "GET":
            self.get(*args, **kwargs)
        elif method == "POST":
            self.post(*args, **kwargs)
        elif method == "DELETE":
            self.delete(*args, **kwargs)
        elif method == "PATCH":
            self.patch(*args, **kwargs)
        elif method == "PUT":
            self.put(*args, **kwargs)
        elif method == "OPTIONS":
            self.options(*args, **kwargs)

    def head(self, *args, **kwargs):
        raise MethodNotAllowed("HEAD")

    def get(self, *args, **kwargs):
        raise MethodNotAllowed("GET")

    def post(self, *args, **kwargs):
        raise MethodNotAllowed("POST")

    def delete(self, *args, **kwargs):
        raise MethodNotAllowed("DELETE")

    def patch(self, *args, **kwargs):
        raise MethodNotAllowed("PATCH")

    def put(self, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def options(self, *args, **kwargs):
        raise MethodNotAllowed("OPTIONS")

    def write_text(self, text, status=200, headers=None,
                   content_type="text/plain; charset=utf-8"):
        http_response = HTTPResponse(
            body=text, status=status, headers=headers,
            content_type=content_type
        )
        self.request.connection.write_response(http_response)
        self._cleanup()

    def write_json(self, body, status=200, headers=None,
                   content_type="application/json", dumps=json_dumps):
        http_response = HTTPResponse(
            body=dumps(body), status=status, headers=headers,
            content_type=content_type
        )
        self.request.connection.write_response(http_response)
        self._cleanup()

    def write_raw(self, body, status=200, headers=None,
                  content_type="application/octet-stream"):
        http_response = HTTPResponse(
            body_bytes=body, status=status, headers=headers,
            content_type=content_type
        )
        self.request.connection.write_response(http_response)
        self._cleanup()

    def _cleanup(self):
        self.request = None








