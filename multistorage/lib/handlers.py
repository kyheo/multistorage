import time
import json
import hashlib
import logging
import threading
import datetime
import functools

from tornado import web

import lib
from lib import workers
from lib.resmanager import ResManager, InvalidId

_ETAGS = []


def exception_handler(fn):
    """Handle exceptions raised in threads
    
    Must be used as decorator of all async callbacks."""
    @functools.wraps(fn)
    def _handler(handler, *args, **kwargs):
        try:
            fn(handler, *args, **kwargs)
        except web.HTTPError, e:
            handler._handle_request_exception(e)
        except Exception, e:
            handler._handle_request_exception(web.HTTPError(500, str(e)))
    return _handler



class BaseHandler(web.RequestHandler):
    """Base class that wraps responses, errors and add stats headers"""
    
    def __init__(self, *args, **kwargs):
        """Store initial time for internal usage"""
        self._start = time.time()
        super(BaseHandler, self).__init__(*args, **kwargs)


    def initialize(self, *args, **kwargs):
        """Check for etag match"""
        inm = self.request.headers.get("If-None-Match")
        if inm in _ETAGS and self.request.method in ['HEAD', 'GET']:
            self._write_buffer = []        
            self.set_status(304) 
        super(BaseHandler, self).initialize(*args, **kwargs)


    def write(self, chunk):
        """Wrap chunk in a dict (to void problems with JSON)"""
        response = {'data': chunk}
        super(BaseHandler, self).write(response)


    def finish(self, *args, **kwargs):
        """Adds X-Stats headers and cache etag"""
        if not self._headers_written:
            self.set_header('X-Stats-Internal', str(time.time() - self._start))
            self.set_header('X-Stats-Tornado', str(self.request.request_time()))

        super(BaseHandler, self).finish(*args, **kwargs)

        if 'Etag' in self._headers and self.request.method in ['HEAD', 'GET']:
            etag = self._headers['Etag'][1:-1]
            logging.debug('Store Etag: %s' % (etag,))
            if etag not in _ETAGS:
                _ETAGS.append(etag)
                # FIXME: Many different url request mean many threads
                # FIXME: TTL should be dynamic
                threading.Timer(15.0, lambda: _ETAGS.remove(etag)).start()


    def get_error_html(self, status_code, **kwargs):
        """Override to implement custom error pages."""
        self.set_header('X-Error', str(kwargs['exception']))
        return super(BaseHandler, self).get_error_html(status_code, **kwargs)




class CollectionHandler(BaseHandler):
    """Handler for collection actions"""

    HANDLED = 0

    def head(self, site, col):
        """ MongoDB will create the database and the collection"""
        CollectionHandler.HANDLED += 1


    @web.asynchronous
    def get(self, site, col):
        CollectionHandler.HANDLED += 1
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col))


    @exception_handler
    def _get(self, site, col):
        list_  = []
        col_   = ResManager.get(site, col)
        params = self._parse_params()
        for entry in col_.find(**params) :
            entry['_id'] = str(entry['_id'])
            list_.append(entry)
        ResManager.end()
        self.write(list_)
        self.finish()


    @web.asynchronous
    def post(self, site, col):
        CollectionHandler.HANDLED += 1
        if self.request.body is None:
            raise web.HTTPError(400, 'Missing new data as JSON dict')
        workers.add(lambda: self._post(site, col))


    @exception_handler
    def _post(self, site, col):
        data = json.loads(self.request.body)
        if '_id' in data:
            del(data['_id'])
        oid = ResManager.get(site, col).save(data)
        ResManager.end()
        self.write(str(oid))
        self.finish()

    
    @web.asynchronous
    def delete(self, site, col):
        CollectionHandler.HANDLED += 1
        workers.add(lambda: self._delete(site, col))


    @exception_handler
    def _delete(self, site, col): 
        ResManager.get(site, col).drop()
        ResManager.end()
        self.finish()


    def _parse_params(self):
        params = {}
        filter_ = self.get_argument('filter', None)
        if filter_ is not None:
            params['filter'] = filter_.split(',')
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
    """Handler for items (aka: rows, entries) actions"""
 
    HANDLED = 0

    @web.asynchronous
    def head(self, site, col, oid):
        ItemHandler.HANDLED += 1
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col,oid, {'fields': {}}))


    @web.asynchronous
    def get(self, site, col, oid):
        ItemHandler.HANDLED += 1
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col, oid))


    @exception_handler
    def _get(self, site, col, oid, extra_args={}):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(oid),
                    **extra_args)
            ResManager.end()
            if i is None:
                raise web.HTTPError(404)
            i['_id'] = str(i['_id'])
            self.write(i)
            self.finish()
        except InvalidId as e:
            raise web.HTTPError(400, str(e))
    
    
    @web.asynchronous
    def delete(self, site, col, oid):
        ItemHandler.HANDLED += 1
        workers.add(lambda: self._delete(site, col, oid))


    @exception_handler
    def _delete(self, site, col, oid):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(oid))
            if i is None:
                ResManager.end()
                raise web.HTTPError(404)
            ResManager.get(site, col).remove(ResManager.oid(oid))
            ResManager.end()
            self.finish()
        except InvalidId as e:
            raise web.HTTPError(400, str(e))
    
    
    @web.asynchronous
    def put(self, site, col, oid):
        ItemHandler.HANDLED += 1
        workers.add(lambda: self._put(site, col, oid))


    @exception_handler
    def _put(self, site, col, oid):
        try:
            i = ResManager.get(site, col).find_one(ResManager.oid(oid))
            if i is None:
                ResManager.end()
                raise web.HTTPError(404)

            data = json.loads(self.request.body)
            if '_id' in data:
                del(data['_id'])
            data['_id'] = ResManager.oid(oid)
            oid = ResManager.get(site, col).save(data)
            ResManager.end()
            self.finish()
        except InvalidId as e:
            raise web.HTTPError(400, str(e))




class StatsHandler(BaseHandler):
    """Handler for stats actions."""
 
    HANDLED = 0

    @web.asynchronous
    def get(self):
        StatsHandler.HANDLED += 1
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get())

    
    def _get(self):
        uptime = datetime.timedelta(seconds=time.time() - lib.START_TIME)
        doc = {}
        doc['Uptime'] = str(uptime) 
        doc['Workers'] = workers.stats()
        doc['RequestHandlers'] = {'CollectionHandler': CollectionHandler.HANDLED,
                                  'ItemHandler'      : ItemHandler.HANDLED      ,
                                  'StatsHandler'     : StatsHandler.HANDLED     ,
                                 }
        self.write(doc)
        self.finish()
