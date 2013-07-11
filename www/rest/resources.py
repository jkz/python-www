"""
Resource defines data and provides the means to manipulate and represent it.

Resources don't know request objects, unless passed as an option!

A resource can have multiple schemas which define the representations.
A resource presents an interface which endpoints use:
    fetch(uid)
    delete(uid)
    replace(uid, representation)
    update(uid, patch)
    create(representation)
    query()
    bulk_delete() / drop()
    bulk_update(patch) / batch(patch)
"""

class Resource:
    def identify(self, representation):
        "Should return identification values for given data"
        raise NotImplementedError

    def filter(self, collection, **options):
        "Return a subset of given collection"
        return collection

    def count(self, collection):
        "Return the entity count of a given collection"
        return len(collection)

    def slice(self, collection, **options):
        return collection[:]


    # Entity
    def fetch(self, uid, **options):
        "Return an entity for given identifier"
        raise NotImplementedError

    def delete(self, uid, **options):
        "Remove an entity by identifier"
        raise NotImplementedError

    def replace(self, uid, representation, **options):
        "Replace or create an entity"
        raise NotImplementedError

    def update(self, uid, patch, **options):
        "Update an identified entity"
        raise NotImplementedError


    # Collection
    def create(self, representation, **options):
        "Create a new entity or collection"
        raise NotImplementedError

    def query(self, **options):
        "Return a filtered entity collection"
        raise responses.NotImplemented

    def bulk_delete(self, **options):
        "Remove a filtered entity collection"
        raise NotImplementedError

    def bulk_update(self, patch, **options):
        "Update each entity of a filtered collection with the same patch"
        raise NotImplementedError

