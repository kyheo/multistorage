import pymongo
from pymongo.errors import InvalidId as InvalidId_Orig

class ResManager(object):

    _INS = None 

    @classmethod
    def get(cls, site, col):
        if ResManager._INS is None:
            ResManager._INS = ResManager(site, col)
        return ResManager._INS.col

    @classmethod
    def end(cls):
        ResManager._INS.con.end_request()

    @classmethod
    def oid(cls, id):
        try:
            return pymongo.objectid.ObjectId(id)
        except Exception as e:
            raise InvalidId(str(e))

    def __init__(self, site, col):
        self.con = pymongo.Connection()
        self.db  = self.con[site]
        self.col = self.db[col]

class InvalidId(InvalidId_Orig):
    pass
