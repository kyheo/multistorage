import json
import urllib
import logging

import pymongo

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
        ResManager.end()

    def delete(self, site, col):
        ResManager.get(site, col).drop()
        ResManager.end()

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

class ItemHandler(BaseHandler):

    def head(self, site, col, id):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(id), fields={})
            ResManager.end()
            if i is None:
                raise tornado.web.HTTPError(404)
        except pymongo.errors.InvalidId as e:
            raise tornado.web.HTTPError(400, str(e))

    def get(self, site, col, id):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(id))
            ResManager.end()
            if i is None:
                raise tornado.web.HTTPError(404)
            i['_id'] = str(i['_id'])
            self.render(item)
        except pymongo.errors.InvalidId as e:
            raise tornado.web.HTTPError(400, str(e))

    def put(self, site, col, id):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(id))
            if i is None:
                ResManager.end()
                raise tornado.web.HTTPError(404)

            data = json.loads(self.request.body)
            if '_id' in data:
                del(data['_id'])
            data['_id'] = ResManager.oid(id)
            id = ResManager.get(site, col).save(data)
            
            ResManager.end()
        except pymongo.errors.InvalidId as e:
            raise tornado.web.HTTPError(400, str(e))

    def delete(self, site, col, id):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(id))
            if i is None:
                ResManager.end()
                raise tornado.web.HTTPError(404)
            ResManager.get(site, col).remove(ResManager.oid(id))
            ResManager.end()
        except pymongo.errors.InvalidId as e:
            raise tornado.web.HTTPError(400, str(e))
