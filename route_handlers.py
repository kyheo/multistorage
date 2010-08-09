import tornado.web
import logging
import time
import json

import output
from resmanager import ResManager

routes = \
   [
    (r"/(0-9a-zA-Z]+/(0-9a-zA-Z]+))/"             , CollectionHandler),
    (r"/(0-9a-zA-Z]+/(0-9a-zA-Z]+))/(0-9a-zA-Z]+)", ItemHandler),
   ]

class CollectionHandler(tornado.web.RequestHandler):

    def head(self, site, collection):
        try:
            ResManager.check(site, collection)
        except (InvalidSite, InvalidCollection) as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))

    def get(self, site, collection):
        try:
            col  = ResManager.get(site, collection)
            list = col.find(self.get_argument('filter', default=None))
        except (InvalidSite, InvalidCollection) as e:
            raise tornado.web.HTTPError(404, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))
        return output.render(list)

    def post(self, site, collection):
        if self.request.body is None:
            raise tornado.web.HTTPError(403, 'Missing new data as JSON dict')
        self.head(site, collection)
        try:
            data = json.loads(self.request.body)
            if '_id' in data:
                del(data['_id'])
            ResManager.get(site, collection).save(data)
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))

    def delete(self, site, collection):
        self.head(site, collection)
        try:
            ResManager.get(site, collection).delete()
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))


class ItemHandler(tornado.web.RequestHandler):

    def head(self, site, collection, id):
        try:
            ResManager.get(site, collection).check(id)
        except ItemNotFound as e:
            raise tornado.web.HTTPError(404, str(e))
        except (InvalidSite, InvalidCollection) as e:
            raise tornado.web.HTTPError(403, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))

    def get(self, site, collection, id, render=True):
        try:
            item = ResManager.get(site, collection).get(id)
        except ItemNotFound as e:
            raise tornado.web.HTTPError(404, str(e))
        except (InvalidSite, InvalidCollection) as e:
            raise tornado.web.HTTPError(403, str(e))
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))
        if render is True:
            return output.render(item)
        else: 
            return item

    def put(self, site, collection, id):
        if self.request.body is None:
            raise tornado.web.HTTPError(403, 'Missing new data as JSON dict')
        item = self.get(site, collection, id, False)
        try:
            data = json.loads(self.request.body)
            if '_id' in data:
                del(data['_id'])
            ResManager.get(site, collection).save(data)
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))

    def delete(self, site, collection, id):
        self.head(site, collection, id)
        try:
            ResManager.get(site, collection).delete(id)
        except Exception as e:
            raise tornado.web.HTTPError(500, str(e))
