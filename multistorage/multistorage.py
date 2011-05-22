#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import logging

from lib import handlers, workers


routes = [(r"/stats/", handlers.StatsHandler),
          (r"/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/", handlers.CollectionHandler),
          (r"/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)/([0-9a-zA-Z]+)", handlers.ItemHandler),
         ]


define('port'   , type=int , default=8000 , help='run on the given port')
define('debug'  , type=bool, default=False, help='enable debug mode'    )
define('no-gzip', type=bool, default=True , help='disables gzip'        )
define('workers', type=int , default=10   , help='asynchronous workers' )


def main():
    """Starts application server"""
    tornado.options.parse_command_line()
    logging.info('Listen on port %d' % (options.port))
    settings = {'gzip': True, 'debug': options.debug}

    workers.start(options.workers)
    try:
        application = tornado.web.Application(routes, **settings)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    finally:
        workers.stop()


if __name__ == "__main__":
    main()
