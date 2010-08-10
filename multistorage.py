#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import logging

from lib.routes_handlers import *


routes = \
   [
    (r"/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/"             , CollectionHandler),
    (r"/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)", ItemHandler),
   ]


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(routes)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    define("port", default=8888, help="run on the given port", type=int)
    main()
