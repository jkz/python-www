"""
Endpoints define the behaviour of http methods on a resource.

A suggested usage pattern is to have resources use fixed interfaces
to make endpoints agnostic and resources pluggable.
"""

import www

from www.server import responses
from . import middleware

class Endpoint(middleware.Endpoint):
    # The methods that are allowed on this endpoint
    methods = www.methods.ALL

    def __init__(self, resource):
        self.resource = resource

    def identify(self, request):
        pass

    def GET(self, request):
        raise www.NotImplemented

    def POST(self, request):
        raise www.NotImplemented

    def PUT(self, request):
        raise www.NotImplemented

    def DELETE(self, request):
        raise www.NotImplemented

    def PATCH(self, request):
        raise www.NotImplemented

    #XXX This is a very naive solution that might run heavy
    #    lookups/logic unnecessarily
    def HEAD(self, request):
        self.GET(request)
        return None

    #XXX Somehow this should find all available options and add them to the
    #    response. The adding of the options metadata could be responsibility
    #    of the options.Option class, this method would then only need to
    #    add them to the response body
    def OPTIONS(self, request):
        response = responses.NoContent()
        response['Allow'] = ', '.join(self.methods)
        raise response

    def resolve(self, request):
        if not request.method in self.methods:
            raise www.MethodNotAllowed

        request['identifier'] = self.identify(request)
        #request['endpoint'] = self

        return getattr(self, request.method)(request)

    def reverse(self, request, **kwargs):
        return request['router'].reverse(self, **kwargs)

    def __repr__(self):
        return 'endpoint {}.{}'.format(self.resource.__class__.__name__,
                self.__class__.__name__)
