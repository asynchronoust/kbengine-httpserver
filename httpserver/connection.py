# -*- coding: utf-8 -*-
"""
FileName:   connection
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
import socket
import errno
from httptools import HttpRequestParser
from httptools.parser.errors import HttpParserError
import traceback
from KBEDebug import *
from multidict import CIMultiDict
from httpserver.request import Request
from httpserver.response import HTTPResponse
from httpserver.exceptions import BaseException_
from httpserver.utils import ERRNO_WOULDBLOCK, errno_from_exception
import KBEngine
from Functor import Functor


class Connection(object):

    def __init__(self, sock, addr, app):
        self._sock = sock
        # addr = (hostaddr, port)
        self._addr = addr
        self._fd = self._sock.fileno()
        self.parser = None
        self.url = None
        self.headers = None
        self._header_fragment = b""
        self.request = None

        self.app = app
        self.has_sent_size = 0
        self.send_body_size = 0
        self._read_buffer = bytearray()
        self._write_buffer = bytes()

    # - on_message_begin()
    # - on_url(url: bytes)
    # - on_header(name: bytes, value: bytes)
    # - on_headers_complete()
    # - on_body(body: bytes)
    # - on_message_complete()
    # - on_chunk_header()
    # - on_chunk_complete()
    # - on_status(status: bytes)

    def get_address(self):
        return self._addr

    def close(self):
        KBEngine.deregisterReadFileDescriptor(self._fd)
        self._sock.close()
        self._fd = 0
        self._sock = None
        self.cleanup()

    def cleanup(self):
        self.request = None
        self.parser = None
        self.headers = []
        self.app = None
        self._read_buffer.clear()
        self._write_buffer = None

    def data_received(self, fd):
        # DEBUG_MSG("data_received, fd: %s, id: %s" % (fd, id(self)))
        if self.parser is None:
            self.parser = HttpRequestParser(self)
            self.headers = []

        while True:
            try:
                data = self._sock.recv(4096)
                # DEBUG_MSG("data_received, fd: %s, data len: %s" %
                #           (fd, len(data)))
                # 客户端关闭了链接
                if not data:
                    ERROR_MSG("data_received, data len is 0, close")
                    self.close()
                    return
                self._read_buffer += data
            except (socket.error, IOError, OSError) as e:
                _errno = errno_from_exception(e)
                # 系统调用被signal中断
                if _errno == errno.EINTR:
                    continue
                # 此次的recv数据读完了，recv抛出下面的异常
                # 此次recv数据读完了，但不表示该连接的一次发包数据读完了，一次发包可能
                # 触发多次epoll 事件
                elif _errno in ERRNO_WOULDBLOCK:
                    DEBUG_MSG("data_received, done")
                    break

                ERROR_MSG("socket recv error: %s" % str(e))
                self.close()
                return
            except Exception as e:
                ERROR_MSG("data_received exception, e: %s" % str(e))
                return

        if self._read_buffer:
            try:
                self.parser.feed_data(bytes(self._read_buffer))
                # 注意要在feed之后清，这次请求可能会被feed 多次，因此每次feed 完要清掉
                self._read_buffer.clear()
            except HttpParserError as e:
                ERROR_MSG(
                    "Connection::data_received feed_data error. error: %s"
                    " \n %s \n id: %s" % (
                        str(e), traceback.format_exc(), id(self)
                    )
                )
                # ERROR_MSG(
                #     "Connection::data_received feed_data error. read_buffer: %s"
                #     " \n" % str(bytes(self._read_buffer))
                #
                # )
                # TODO 给客户端回错误

    def on_url(self, url):
        if not self.url:
            self.url = url
        else:
            self.url += url

    def on_header(self, key, value):
        """
        :param key:
        :param value: bytes
        :return:
        """
        self._header_fragment += key
        if value is not None:
            try:
                value = value.decode()
            except UnicodeDecodeError:
                value = value.decode("latin_1")

            self.headers.append(
                (self._header_fragment.decode().casefold(), value)
            )

            self._header_fragment = b""

    def on_headers_complete(self):
        DEBUG_MSG("Connection::on_header_complete")
        self.request = Request(
            url_bytes=self.url,
            headers=CIMultiDict(self.headers),
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode(),
            connection=self,
        )

    def on_body(self, data):
        DEBUG_MSG("Connection::on_body, data len: %s" % len(data))
        # DEBUG_MSG("data: %s" % str(data))
        self.request.body.append(data)

    def on_message_complete(self):
        INFO_MSG("Connection request: %s" % str(self.request))
        self.request.body = b"".join(self.request.body)
        self.handle_request()

    def handle_request(self):
        request_handler_class = self.app.router.get(self.request.path)
        if not request_handler_class:
            response = HTTPResponse(
                "NotFound handler", status=500
            )
            self.write_response(response)
            return

        try:
            handler = request_handler_class(self.request)
            # TODO url 参数等数据后面加上
            handler.execute_handler()
        except BaseException_ as e:
            response = HTTPResponse(
                "An error occurred, error: %s" % str(e),
                status=e.status_code or 500
            )
            self.write_response(response)
        except Exception as e:
            ERROR_MSG("Internal Server Error: %s" % str(e))
            response = HTTPResponse(
                "Internal Server Error", status=500
            )
            self.write_response(response)

    def write_response(self, response):
        self._write_buffer = response.output()
        self.send_body_size = len(self._write_buffer)
        self._write_to_fd(False, self._fd)
        if self._check_send_finish():
            self.write_completed()
        else:
            # 一次没有发完，注册fd，交给epoll
            DEBUG_MSG("Connection::register write fd: %s" % self._fd)
            KBEngine.registerWriteFileDescriptor(
                self._fd, Functor(self._write_to_fd, True)
            )

    def _write_to_fd(self, in_poller, fd):
        try:
            send_size = self._sock.send(self._write_buffer[self.has_sent_size:])
            self.has_sent_size += send_size
            DEBUG_MSG("_write_to_fd, in_poller: %s, fd: %s" % (in_poller, fd))
            if in_poller and self._check_send_finish():
                self.write_completed(in_poller)
        except (socket.error, IOError, OSError) as e:
            ERROR_MSG("write to fd error: %s" % str(e))
            self.close()

    def _check_send_finish(self):
        return self.has_sent_size >= self.send_body_size

    def write_completed(self, in_poller=False):
        if in_poller:
            KBEngine.deregisterWriteFileDescriptor(self._fd)

        DEBUG_MSG("write_completed, in_poller: %s, fd: %s" %
                  (in_poller, self._fd))
        self.close()




