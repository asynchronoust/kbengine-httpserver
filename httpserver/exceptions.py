# -*- coding: utf-8 -*-
"""
FileName:   exceptions
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/30

Description:

Changelog:
"""


def add_status_code(code):
    def class_decorator(cls):
        cls.status_code = code
        return cls

    return class_decorator


class BaseException_(Exception):

    def __init__(self, message, status_code=None):
        super(BaseException_, self).__init__(message)
        self.status_code = None
        if status_code is not None:
            self.status_code = status_code


@add_status_code(400)
class InvalidUsage(BaseException_):
    pass


class UriDuplicated(BaseException_):
    pass


@add_status_code(405)
class MethodNotAllowed(BaseException_):
    def __init__(self, method):
        msg = "method: %s not allowed" % method
        super(MethodNotAllowed, self).__init__(msg)


@add_status_code(404)
class NotFound(BaseException_):
    def __init__(self, uri):
        msg = "uri: %s not found" % uri
        super(NotFound, self).__init__(msg)


if __name__ == "__main__":
    e = InvalidUsage("test")

