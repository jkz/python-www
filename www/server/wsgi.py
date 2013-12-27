import functools
import wsgiref

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

from www.server import http, stack
from www.utils.functions import header_case

def extract(env, key):
    """Extract a key from a wsgi environment and converts it to unicode"""
    #TODO: make this worthwile, or remove it
    try:
        return str(env[key])
    except KeyError:
        return None

def parse(env):
    """
    Create a http.Request from given wsgi environment.
    All values are added by their keys into the request.
    All headers are stored in Header-Case in request.headers.
    The body is passed the file in 'wsgi.input'
    """
    url = wsgiref.util.request_uri(env)
    method = extract(env, 'REQUEST_METHOD')

    headers = http.Header()
    headers['Content-Length'] = extract(env, 'CONTENT_LENGTH')
    headers['Content-Type'] = extract(env, 'CONTENT_TYPE')

    body = env['wsgi.input']

    request = http.Request(url, method=method, body=body, headers=headers)

    for key, val in env.items():
        if key.startswith('HTTP_'):
            request.headers[header_case(key)] = str(val)
        request[key] = str(val)

    return request

def application(app):
    """
    Wrap a www application callable which takes a request object as its single
    argument.
    """
    @functools.wraps(app)
    def func(environ, start_response, extra=None):
        request = parse(environ)
        response = app(request)
        start_response(response.status, response.headers)
        return list(response.body)
    return func

class Application:
    """
    Wrap a www application callable which takes a request object as its single
    argument.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = parse(environ)
        response = self.app(request)
        start_response(response.status, response.headers)
        return list(response.body)

class Server(stack.Server):
    def wsgi_application(self, environ, start_response):
        """Compatible with both www and wsgi applications"""
        request = parse(environ)
        print(79 * '=')
        print(str(request))
        response = self.resolve(request)
        print('RESPONSE', response)
        print('STATUS', response.status)
        print('HEADERS', response.headers)
        print('BODY', response.body)
        start_response(response.status, list(response.headers.items()))
        return list(response.body.iterbytes())

    def make(self, app=None):
        return make_server(self.authority.host, self.authority.port,
                app or self.wsgi_application)

    def forever(self, app=None):
        print('{} - Serving forever!'.format(self.authority))
        self.make(app).serve_forever()

    def once(self, app=None):
        print('{} - Handling next request.'.format(self.authority))
        self.make(app).handle_request()

    def serve(self, app=None, forever=True):
        self.forever(app) if forever else self.once(app)


def server(host, port, *args, **kwargs):
    return Server(host, port, stack.build(*args, **kwargs))

def serve(host, port, *args, forever=True, **kwargs):
    server(host, port, *args, **kwargs).serve(forever=forever)

def setup_environ(**kwargs):
    """
    Create a default wsgi environment, for testing purposes.
    """
    env = {}
    setup_testing_defaults(env)
    env.update(kwargs)
    return env
