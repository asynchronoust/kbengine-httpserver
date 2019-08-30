# -*- coding: utf-8 -*-
"""
FileName:   server
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
import KBEngine
from KBEDebug import *
import socket
from httpserver.connection import Connection


class Server(object):

    def __init__(self, app):
        self._socket = None
        self._host = None
        self._port = None
        self._fd = 0
        self.app = app

    def run(self, host, port, backlog=128):
        INFO_MSG("httpserver run, host[%s], post[%s]..." % (host, port))
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            ERROR_MSG("server run socket error: %s" % str(e))
            raise

        self._socket.setblocking(False)
        self._socket.bind((host, port))
        self._socket.listen(backlog)
        self._set_server_fd()
        self._host = host
        self._port = port
        KBEngine.registerReadFileDescriptor(self._fd, self.accept)

    def _set_server_fd(self):
        self._fd = self._socket.fileno()

    def accept(self, fd):
        if fd != self._fd:
            ERROR_MSG("Server::accept, fd[%s] is not _fd[%s]" % (fd, self._fd))
            return

        # addr = (hostaddr, port)
        sock, addr = self._socket.accept()
        # 设置为unblocking
        sock.setblocking(False)
        socket_fd = sock.fileno()
        new_conn = Connection(sock, addr, self.app)
        DEBUG_MSG("Server::accept, new connection[%s], addr[%s], fd[%s]" %
                  (id(new_conn), addr, socket_fd))
        KBEngine.registerReadFileDescriptor(
            socket_fd, new_conn.data_received
        )

    def stop(self):
        if self._socket:
            INFO_MSG(
                "httpserver stop host[%s], port[%s]" % (self._host, self._port)
            )
            KBEngine.deregisterReadFileDescriptor(self._fd)
            self._socket.close()
            self._socket = None
            self.app = None




