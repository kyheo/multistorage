#!/usr/bin/env python

import time
import httplib
import json
import optparse

import pprint


def make_request(options):
    params = None
    if options.data:
        params = options.data

    headers = {}
    if options.etag:
        headers['If-None-Match'] = options.etag

    print 'Request', "http://%s:%d%s" % (options.server, options.port,
            options.url)
    conn = httplib.HTTPConnection(options.server, options.port)
    conn.request(options.method, options.url, params, headers)
    res = conn.getresponse()
    print res.status, res.reason
    print 'Headers: '
    pprint.pprint(res.getheaders())
    data = res.read() 
    if data:
        print 'Body: ' 
        if res.status == 200:
            pprint.pprint(json.loads(data))
        else:
            print data
    conn.close()


if __name__=='__main__':
    start = time.time()
    parser = optparse.OptionParser()
    parser.add_option('-s', '--server', dest='server', type='string', default='127.0.0.1', help='Service host (ex: 127.0.0.1)')
    parser.add_option('-p', '--port'  , dest='port'  , type='int'   , default=8000       , help='Service port (ex: 8000)')
    parser.add_option('-m', '--method', dest='method', type='string', default='GET'      , help='HTTP Method (HEAD, GET, PUT, POST or DELETE)')
    parser.add_option('-u', '--url'   , dest='url'   , type='string'                     , help='Resource (ex: /itemstore/sites/)')
    parser.add_option('-d', '--data'  , dest='data'  , type='string', default=None       , help='JSON to be sent to the service, useful for PUT and POST requests.')
    parser.add_option('-e', '--etag'  , dest='etag'  , type='string', default=None       , help='Request Etag.')
    make_request(parser.parse_args()[0])
    print 'In caller: ', time.time() - start
