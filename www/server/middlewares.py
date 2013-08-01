import functools

from www.core import exceptions
from www.server import responses
from www.content import serialize, deserialize
from .middleware import Middleware, Stack, Option
from . import wsgi

def api(router):
    def decorate(app):
        @functools.wraps(app)
        def func(request):
            request['router'] = router
            return app(request)
        return func
    return decorate

class Entry:
    def __init__(self, router):
        self.router = router

    def __call__(self, app):
        @functools.wraps(app)
        def application(request):
            request['router'] = self.router
            return app(request)
        return application


class Router(Option):
    def resolve(self, request):
        try:
            endpoint, kwargs = request['router'].resolve(request.path)
        #404
        except TypeError:
            raise responses.NotFound()

        request['endpoint'] = endpoint
        request['kwargs'] = kwargs

class Dispatcher(Middleware):
    def resolve(self, request):
        return request['endpoint'](request)

def dispatch(request):
    request['method'] = request.url.query.get('method', request.method)
    return request['endpoint'].resolve(request)


def Tryer(app):
    @functools.wraps(app)
    def func(request):
        try:
            return app(request)
        except responses.Response as response:
            return response
        except exceptions.Fault as fault:
            print('FAULT', fault)
        except exceptions.Error as error:
            print('ERROR', error)
        except exceptions.Warning as warning:
            print('WARNING', warning)
        except Exception as e:
            print('EXCEPTION', e)
        return 'EXCEPTION'
    return func

class Server(wsgi.Server):
    def __init__(self, host, port, router):
        super().__init__(host, port)
        self.router = router


import json
def server(host, port, router, *apps):
    *apps = apps
    stack = Stack((Entry(router), Router) + apps)(dispatch)
    return wsgi.server(host, port, stack)


Negotiator = object

class Accept(Negotiator):
    as_kwarg  = 'ext'
    as_query  = 'format'

    help_text = "The response data format"

    @property
    def as_header(self):
        return ('Accept', lambda self, header: accept_header(self.field.choices, header))


class ContentType(Negotiator):
    as_query  = 'content_type'

    help_text = "The request data format"

    @property
    def as_header(self):
        return ('Content-Type', lambda self, header:
                content_type(self.field.choices, header))


class Language(Negotiator):
    as_kwarg  = 'lang'
    as_query  = 'lang'
    as_header = 'Accept-Language'

    help_text = "The response data language"

class Content(Middleware):
    def resolve(self, request, response):
        request['data'] = deserialize(request.body, request['Content-Type'])
        data = self.application(request, response)
        serialized = serialize(data, response['Content-Type'])
        response['Content-Length'] = len(serialized)
        return serialized

class Deserialize(Middleware):
    def resolve(self, request, response):
        request['data'] = deserialize(request.body,
                request['Content-Type'])
        return self.application(request, response)


class Serialize(Middleware):
    def resolve(self, request, response):
        data = self.application(request, response)
        serialized = serialize(data, response['content-type'])
        response['Content-Length'] = len(serialized)
        return serialized

content = Stack([
    Accept,
    Language,
    ContentType,
    Content,
])



Stack([
    Tryer,
    Router,
    Content,
])

