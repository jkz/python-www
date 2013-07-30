import functools
import wsgiref
from wsgiref.util import setup_testing_defaults

from www.core import http
from www.utils.functions import header_case

def extract(env, key):
    """Extract a key from a wsgi environment"""
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
    def func(environ, start_response):
        request = parse(environ)
        response = app(request)
        start_response(response.status, response.headers)
        return list(response.body)
    return func

class Application:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = parse(environ)
        response = app(request)
        start_response(response.status, response.headers)
        return list(response.body)

class Server:
    def __init__(self, authority, app):
        self.authority = authority
        self.app = app

    @application
    def application(self, request):
        """Compatible with both www and wsgi applications"""
        request.authority = self.authority
        return self.app(request)


    def serve(self, forever=True):
        server = wsgiref.make_server(self.authority.host, self.authority.port,
                self.application)
        if forever:
            server.serve_forever()
        else:
            server.handle_request()

    def forever(self):
        return self.serve(forever=True)

    def once(self):
        return self.serve(forever=False)


def server(host, port, app):
    authority = http.Authority(host=host, port=port)
    return Server(authority=authority, app=app)

def serve(host, port, app, forever=True):
    server(host, port, app).serve(forever)

def setup_environ(**kwargs):
    """
    Create a default wsgi environment, for testing purposes.
    """
    env = {}
    setup_testing_defaults(env)
    env.update(kwargs)
    return env
