import functools
import base64

from www.core import http

from . import Error, Auth, Consumer, Token, Service

class Error(Error):
    pass


class Auth(Auth):
    def encode_pair(self, username, password):
        pair = '{}:{}'.format(username, password).encode(self.encoding)
        b64pair = base64.b64encode(pair)
        return 'Basic {}'.format(b64pair.decode())


    def decode_pair(self, header):
        if not header[:6] == ('Basic '):
            raise Error('Non-Basic Authorization')
        pair = header[6:]
        b64pair = base64.b64decode(pair)
        return dict(zip(('username', 'password'), b64pair.split(':', 2)))

    def __init__(self, consumer=None, token=None, encoding='ISO-8859-1', **options):
        self.consumer = consumer
        self.token = token
        self.encoding = encoding
        self.options = options

    def __call__(self, request):
        """
        Return signed request parameters.
        """
        if self.token:
            request.headers['Authorization'] = self.encode_pair(
                    self.token.username, self.token.password)

class Service(Service):
    pass


class Consumer(Consumer): pass

class Token(Token):
    def __init__(self, username, password):
        self.username = username
        self.password = password


def create_request(*args, **kwargs):
    token = Token(kwargs.pop('username'), kwargs.pop('password'))
    request = http.Request(*args, **kwargs)
    auth = Auth(token=token)
    request.processors.append(auth)
    return request

www.implement_methods(create_request, globals())
