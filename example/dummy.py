from www.client.resources import Resource

class DB:
    def __init__(self):
        self.dbs = {}

    def __get__(self, obj, cls):
        if not obj.name in self.dbs:
            self.dbs[obj.name] = {}
        return self.dbs[obj.name]

    def __set__(self, obj, val):
        self.dbs[obj.name] = val

    def __del__(self, obj):
        del self.dbs[obj.name]


class Dummy(Resource):
    db = DB()
    last_uid = 0

    def new_uid(self):
        self.last_uid += 1
        return self.last_uid

    def identify(self, object):
        return object['uid']

    def _filter(self, collection, key, value):
        for entity in collection:
            if entity[key] == value:
                yield collection

    def filter(self, collection, **options):
        for key, val in options.items():
            collection = self._filter(collection, key, val)
        return list(collection)


    # Entity
    def fetch(self, uid):
        uid = int(uid)
        return copy.deepcopy(self.db[uid])

    def delete(self, uid):
        del self.db[uid]

    def replace(self, uid, representation):
        self.db[uid] = copy.deepcopy(representation)

    def update(self, uid, patch):
        for key, val in patch.items():
            self.db[uid][key] = val

    # Collection
    def query(self, filters):
        return list(self.db.values())

    def create(self, representation):
        uid = self.new_uid()
        self.replace(uid, representation)
        return uid

    def drop(self, filters):
        self.db = {}

    def batch(self, patch, **options):
        for uid in self.db:
            self.update(uid, patch)
