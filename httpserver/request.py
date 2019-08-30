# -*- coding: utf-8 -*-
"""
FileName:   request
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
from httptools import parse_url
import json
from httpserver.exceptions import InvalidUsage
from urllib.parse import parse_qs, urlunparse

try:
    from ujson import loads as json_loads
except ImportError:
    json_loads = json.loads


DEFAULT_HTTP_CONTENT_TYPE = "application/octet-stream"


class RequestParameters(dict):

    def get(self, name, default=None):
        return super(RequestParameters, self).get(name, [default])[0]

    def getlist(self, name, default=None):
        return super(RequestParameters, self).get(name, default)


class Request(object):

    def __init__(self, url_bytes, headers, version, method, connection):
        self._ip = ""
        self._port = 0
        self._remote_addr = None
        self.raw_url = url_bytes
        # _parse_url has following properties
        # - schema: bytes
        # - host: bytes
        # - port: int
        # - path: bytes
        # - query: bytes
        # - fragment: bytes
        # - userinfo: bytes
        self._parsed_url = parse_url(url_bytes)

        self.headers = headers
        self.version = version
        self.method = method
        self.connection = connection
        self.set_address_info()

        self.body = []
        self.parsed_json = None
        self.parsed_form = None
        self.parsed_args = None

    def __repr__(self):
        if self.method is None or not self.path:
            return "<{0}>".format(self.__class__.__name__)

        return "<{0}: {1} {2}>".format(
            self.__class__.__name__, self.method, self.path)

    def set_address_info(self):
        self._ip, self._port = self.connection.get_address()

    @property
    def json(self):
        if self.parsed_json is None:
            self.load_json()

        return self.parsed_json

    def load_json(self, loads=json_loads):
        try:
            self.parsed_json = loads(self.body)
        except Exception:
            if not self.body:
                return None

            raise InvalidUsage("load body json error")

        return self.parsed_json

    @property
    def args(self):
        if self.parsed_args is None:
            if self.query_string:
                self.parsed_args = RequestParameters(
                    parse_qs(self.query_string, keep_blank_values=True)
                )
            else:
                self.parsed_args = RequestParameters()

        return self.parsed_args

    @property
    def query_string(self):
        if self._parsed_url.query:
            return self._parsed_url.query.decode("utf-8")
        else:
            return ""

    @property
    def path(self):
        return self._parsed_url.path.decode("utf-8")

    @property
    def host(self):
        return self.headers.get("Host", "")

    @property
    def content_type(self):
        return self.headers.get("Content-Type", DEFAULT_HTTP_CONTENT_TYPE)

    @property
    def scheme(self):
        return "http"

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def remote_addr(self):
        if getattr(self, "_remote_addr", None) is None:
            forwarded_for = self.headers.get("X-Forwarded-For", "").split(",")
            remote_addrs = [
                addr for addr in [addr.stip() for addr in forwarded_for] if addr
            ]
            if len(remote_addrs):
                self._remote_addr = remote_addrs[0]
            else:
                self._remote_addr = ""

        return self._remote_addr

    @property
    def url(self):
        return urlunparse(
            (self.scheme, self.host, self.path, None, self.query_string, None)
        )



