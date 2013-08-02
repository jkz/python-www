import functools

from www.core import exceptions
from www.content import serialize, deserialize
from . import http, middleware, responses

class Excepts(middleware.Layer):
    def resolve(self, request):
        try:
            return responses.Ok(self.application(request))
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
            raise
        return 'EXCEPTION'


def Router(routes):
    class Router(middleware.Option):
        def resolve(self, request):
            try:
                endpoint, kwargs = routes.resolve(request.path)
            #404
            except TypeError:
                raise responses.NotFound()

            request['router'] = routes
            request['endpoint'] = endpoint
            request['kwargs'] = kwargs
    return Router



class Deserialize(middleware.Layer):
    def resolve(self, request):
        if request.method in {'PUT', 'POST', 'PATCH'}:
            request['data'] = deserialize(request.content, request.content_type)
        return self.application(request)


class Serialize(middleware.Layer):
    def resolve(self, request):
        data = self.application(request)
        return serialize(data, request.accept)


class Authenticate(middleware.Option):
    def credentials(self, request):
        return {}

    def authenticate(self, **creds):
        return None

    def resolve(self, request):
        creds = self.credentials(request)
        request['auth'] = self.authenticate(**creds)


class Session(middleware.Option):
    def get_session(self, reqeust):
        return None

    def resolve(self, request):
        request['session'] = self.get_session(request)


Content = middleware.Stack([
    Serialize,
    Deserialize,
])

class Dispatcher(middleware.Endpoint):
    def resolve(self, request):
        return request['endpoint'](request)

def build(router, *stack, dispatcher=Dispatcher()):
    base = middleware.Stack([
        Excepts,
        Router(router),
        Content,
    ])
    extra = middleware.Stack(stack)
    return (base + extra)(dispatcher)


class Server:
    def __init__(self, host, port, application):
        self.authority = http.Authority(host, port)
        self.application = application

    def resolve(self, request):
        request.authority = self.authority
        return self.application(request)

def server(host, port, *args, **kwargs):
    return Server(host, port, build(*args, **kwargs))
