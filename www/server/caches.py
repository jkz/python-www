from . import middleware
from . import responses

class SimpleCache()

class Etag(middleware.Cache):
    def key(self, request):
        return request['If-Modified-Since']

    def get(self):
        pass

    def set(self):
        pass

class IfModifiedSince(middleware.Guard):
    def resolve(self, request):
        if

class Headers(middleware.Option):
    def if_modified_since(self, request):
        if 'If-Modified-Since' in request.headers:
            request['

            If-Match
            If-Modified-Since
            If-None-Match
            If-Range
            If-Unmodified-Since

    def resolve(self, request):
