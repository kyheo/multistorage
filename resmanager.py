import pymongo

class ResManager(object):
    _CON = None

    @classmethod
    def check(cls, site, collection):
        ResManager._get(site, collection, False)

    @classmethod
    def get(cls, site, collection):
        return ResManager._get(site, collection)

    @classmethod
    def _get(cls, site, collection, res=True):
        if ResManager._CON is None:
            ResManager._CON = pymongo.Connection()
        if site not in ResManager._CON:
            raise InvalidSite(site)
        db = ResManager._CON[site]
        if collection not in db:
            raise InvalidCollection(collection)
        if res is True:
            return Collection.singleton(db, collection)

class Collection(object):

    _INSTANCE = None

    def __init__(self, col):
        self._col = col

    @classmethod
    def singleton(cls, db, col):
        if Collection._INSTANCE is None:
            Collection._INSTANCE = Collection(db[col])
        return Collection._INSTANCE



"""Exceptions"""
class InvalidSite(Exception):
    pass

class InvalidCollection(Exception):
    pass

class ItemNotFound(Exception):
    pass
