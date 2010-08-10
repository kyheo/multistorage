import json
import urllib

import tornado.web

from lib.basehandler import BaseHandler 
from lib.resmanager import ResManager

class CollectionHandler(BaseHandler):

    def head(self, site, col):
        """ MongoDB will create the database and the collection
        """
        pass

    def get(self, site, col):
        list   = []
        col    = ResManager.get(site, col)
        params = self._parse_params()
        for entry in col.find(**params) :
            entry['_id'] = str(entry['_id'])
            list.append(entry)
        ResManager.end()
        self.render(list)

    def post(self, site, col):
        if self.request.body is None:
            raise tornado.web.HTTPError(403, 'Missing new data as JSON dict')
        data = json.loads(self.request.body)
        if '_id' in data:
            del(data['_id'])
        id = ResManager.get(site, col).save(data)
        ResManager.end()
        self.render(str(id))

    def delete(self, site, col):
        self.head(site, col)
        ResManager.get(site, col).drop()

    def _parse_params(self):
        params = {}
        filter = self.get_argument('filter', None)
        if filter is not None:
            params['filter'] = filter.split(',')
        fields = self.get_argument('fields', None)
        if fields is not None:
            params['fields'] = fields.split(',') 
        sort = self.get_argument('sort', None)
        if sort is not None:
            params['sort'] = sort.split(',')
        skip = self.get_argument('skip', None)
        if skip is not None:
            params['skip'] = int(skip)
        limit = self.get_argument('limit', None)
        if limit is not None:
            params['limit'] = int(limit)
        return params


