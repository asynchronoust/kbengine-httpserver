# -*- coding: utf-8 -*-
"""
FileName:   router
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/29

Description:

Changelog:
"""
from httpserver.exceptions import MethodNotAllowed, NotFound, UriDuplicated


class Router(object):

    """
    TODO 1.优化router, 2.加上正则表达式, 3.uri中加入变量支持
    """

    def __init__(self):
        self.routes_all = {}

    def add(self, uri, handler):
        if uri not in self.routes_all:
            self.routes_all[uri] = handler
        else:
            raise UriDuplicated("uri: %s is duplicated" % uri)

    def get(self, uri):
        return self.routes_all.get(uri)


