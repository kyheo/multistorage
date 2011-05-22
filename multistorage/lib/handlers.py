import time
import json
import hashlib
import logging
import threading

from tornado import web

from lib import workers
from lib.resmanager import ResManager, InvalidId

_ETAGS = []

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

        if 'Etag' in self._headers:
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

    def head(self, site, col):
        """ MongoDB will create the database and the collection"""
        pass


    @web.asynchronous
    def get(self, site, col):
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col))


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
 
    @web.asynchronous
    def head(self, site, col, oid):
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col,oid, {'fields': {}}))


    @web.asynchronous
    def get(self, site, col, oid):
        if self.get_status() == 304:
            return
        workers.add(lambda: self._get(site, col, oid))


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
