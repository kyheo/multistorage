import pymongo

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
        return pymongo.objectid.ObjectId(id)

    def __init__(self, site, col):
        self.con = pymongo.Connection()
        self.db  = self.con[site]
        self.col = self.db[col]
