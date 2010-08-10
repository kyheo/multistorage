import tornado.web
import json

class BaseHandler(tornado.web.RequestHandler):

    def render(self, data):
        self.set_header("Content-Type", "text/json")
        self.write(json.dumps(data, indent=4))
