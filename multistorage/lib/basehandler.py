import httplib
import json

import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    def render(self, data):
        self.set_header("Content-Type", "text/json")
        self.write(json.dumps(data, indent=4))

    def get_error_html(self, status_code, **kwargs):
        """Override to implement custom error pages.                                                                                         

           If this error was caused by an uncaught exception, the
           exception object can be found in kwargs e.g.
           kwargs['exception']                                                                     
        """
        self.set_header('X-Error', str(kwargs['exception']))
        return tornado.web.RequestHandler.get_error_html(self, status_code,
                                                         **kwargs)
