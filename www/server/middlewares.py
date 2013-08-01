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


class Deserialize(Middleware):
    def resolve(self, request):
        request['data'] = deserialize(request.body, request.content_type)
        return self.application(request)


class Serialize(Middleware):
    def resolve(self, request):
        data = self.application(request)
        return serialize(data, request.accept)


content = Stack([
    Serialize,
    Deserialize,
])


Stack([
    Tryer,
    Router,
    Content,
])
