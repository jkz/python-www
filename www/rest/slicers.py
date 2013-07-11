import www

from www.core import options
from www.core import fields

from . import structures

class Limit(options.Option):
    "The maximum collection size returned"
    as_query = 'limit',
    field = fields.Integer(
        min = 1
        max = None
        default = 20
    )

class Offset(options.Option):
    "The maximum collection size returned"
    as_query = 'offset',
    field = fields.Integer(
        min = 0
        max = None
        default = min
    )

class Page(options.Option):
    "The maximum collection size returned"
    as_query = 'page',
    field = fields.Integer(
        min = 1
        max = None
        default = min
    )

class Size(options.Option):
    "The maximum collection size returned"
    as_query = 'size',
    field = fields.Integer(
        min = 0
        max = None
        default = 20
    )


class Slice(structures.NestedClass):
    """An offset/limit slicer"""
    silent = False

    unlimited = 'none'

    count_key = 'count'

    next_key = 'next'
    prev_key = 'prev'

    msg_invalid = "Must be an integer"
    msg_under = "Can't be less than {min}"
    msg_over = "Can't be more than {max}"

    options = options.Options(
        limit = Limit(),
        offset = Offset(),
    )

    @property
    def indexing(self):
        return self.options['offset'].min

    def get_uri(self, request, limit, offset):
        query = {self.limit_key: limit, self.offset_key: offset}
        return www.URL(request.location(), query=query)

    def get_prev(self, request, limit, offset):
        if limit and offset - limit >= self.indexing:
            return self.get_uri(request, limit, offset - limit)

    def get_next(self, request, limit, offset, count):
        if limit and offset + limit < count:
            return self.get_uri(request, limit, offset + limit)

    def get_slice(self, collection, limit=None, offset=None):
        offset = offset - self.indexing or 0
        if limit is None:
            return collection[offset:]
        else:
            return collection[offset:offset + limit]

    def __call__(self, request, collection):
        count = self.get_count(collection)

        info = {
            self.count_key: count,
        }

        limit = request['limit']
        offset = request['offset']

        collection = self.get_slice(collection, limit, offset)

        if offset:
            info[self.offset_key] = offset

        if limit:
            info[self.limit_key] = limit

        prev = self.get_prev(request, limit, offset)
        if prev:
            info[self.prev_key] = prev

        next = self.get_next(request, limit, offset, count)
        if next:
            info[self.next_key] = next

        return collection, info


class Paginate(Slice):
    options = options.Options(
        limit = Size(),
        offset = Page()
    )

    def get_prev(self, request, limit, offset):
        if offset > self.indexing:
            return self.get_uri(request, limit, offset - 1)

    def get_next(self, request, size, page, count):
        if page * size < count:
            return self.get_uri(request, size, page + 1)

    def get_slice(self, collection, limit=None, offset=None):
        offset = 0 if offset is None else (offset - self.indexing) * offset
        if limit is None:
            return collection[offset:]
        else:
            return collection[offset:offset + limit]

