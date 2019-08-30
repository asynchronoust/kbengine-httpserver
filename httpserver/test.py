# -*- coding: utf-8 -*-
"""
FileName:   test
Author:     Tao Hao
@contact:   taohaohust@outlook.com
Created time:   2019/5/30

Description:

Changelog:
"""
from httpserver.app import Application, RequestHandler


class IndexHandler(RequestHandler):

    def get(self, *args, **kwargs):
        print("index, get")
        self.write_text("index ok")


class HomeHandler(RequestHandler):

    def get(self, *args, **kwargs):
        print("home, get")
        self.write_text("home ok")

    def post(self, *args, **kwargs):
        # DEBUG_MSG("post body, %s" % str(self.request.json))
        self.write_json(self.request.json)


app = None


def run_server():
    url_map = [
        ("/index", IndexHandler),
        ("/home", HomeHandler)
    ]
    _app = Application(url_map)
    _app.run("0.0.0.0", 9191)
    global app
    app = _app
    return _app








