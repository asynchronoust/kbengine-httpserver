# -*- coding: utf-8 -*-
"""
FileName:   response
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
from multidict import CIMultiDict
from httpserver.utils import remove_entity_headers, STATUS_CODES


class HTTPResponse(object):

    def __init__(self, body=None,
                 status=200, headers=None,
                 content_type="text/plain", body_bytes=b""):
        self.content_type = content_type
        self.headers = headers

        if body is not None:
            self.body = self.encode_body(body)
        else:
            self.body = body_bytes

        self.status = status
        self.headers = CIMultiDict(headers or {})

    def encode_body(self, data):
        try:
            return data.encode()
        except AttributeError:
            return str(data).encode()

    def parse_headers(self):
        headers = b""
        for key, value in self.headers.items():
            try:
                headers += b"%b: %b\r\n" % (key.encode(), value.encode("utf-8"))
            except AttributeError:
                headers += b"%b: %b\r\n" % (
                    str(key).encode(), str(value).encode("utf-8")
                )

        return headers

    def has_message_body(self):
        """
        According to the following RFC message body and length SHOULD NOT
        be included in responses status 1XX, 204 and 304.
        https://tools.ietf.org/html/rfc2616#section-4.4
        https://tools.ietf.org/html/rfc2616#section-4.3
        """
        return self.status not in (204, 304) and not (100 <= self.status < 200)

    def output(self, version="1.1", keep_alive=False, keep_alive_timeout=None):
        """
        TODO 先暂时不支持 keep alive
        :param version:
        :return:
        """
        timeout_header=b""
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b"Keep-Alive: %d\r\n" % keep_alive_timeout

        body = b""
        if self.has_message_body():
            body = self.body
            self.headers["Content-Length"] = self.headers.get(
                "Content-Length", len(self.body)
            )

        self.headers["Content-Type"] = self.headers.get(
            "Content-Type", self.content_type
        )

        if self.status in (304, 412):
            self.headers = remove_entity_headers(self.headers)

        headers = self.parse_headers()

        if self.status == 200:
            status_msg = b"OK"
        else:
            status_msg = STATUS_CODES.get(self.status, b"UNKNOWN RESPONSE")

        """
        消息结构如下：
        HTTP/1.1 200 OK                     # 状态行
        Connection: close                   # headers
        Content-Type: text/plain
                                            # 空行
        xxxxxbody part                      # body内容
        """
        return (
            b"HTTP/%b %d %b\r\n" b"Connection: %b\r\n" b"%b" b"%b\r\n" b"%b"
        ) % (
            version.encode(),
            self.status,
            status_msg,
            b"keep-alive" if keep_alive else b"close",
            timeout_header,
            headers,
            body
        )







