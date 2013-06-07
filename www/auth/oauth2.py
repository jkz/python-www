import www

from www import auth

class Error(auth.Error): pass

class Connection(www.Connection): pass

class Consumer(auth.Consumer):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret


class Token(auth.Token):
    def __init__(self, key):
        self.key = key

class Auth(auth.Auth):
    """
    An OAuth 2 authenticator. Is associated with a client which can
    authenticate and register end users. If an enduser is associated with this
    authenticator, it can authorize requests.
    """
    def __call__(self, request):
        """
        Add a token parameter tot the query string.

        Heads up!

        Does not support duplicate keys.
        """
        if self.token is not None:
            request.resource.query['access_token'] = self.token.key
        else:
            request.resource.query['client_id'] = self.consumer.key


class Service(auth.service):
    pass

class Authority(Service):
    AUTHENTICATE_URL = NotImplemented

    EXCHANGE_CODE_PATH = NotImplemented

    def request_code(self, redirect_uri, **kwargs):
        """Return a redirect url"""
        query = {
                'client_id': self.auth.consumer.key,
                'redirect_uri': redirect_uri,
        }
        query.update(kwargs)
        return www.URL(self.AUTHENTICATE_URL, verbatim=False, **query)

    def exchange_code(self, code, redirect_uri, **kwargs):
        """
        Trade a code for access credentials. They are returned as a
        www.Response object, to be parsed by the caller.
        """
        response = self.connection.POST(
                self.EXCHANGE_CODE_PATH,
                code=code,
                redirect_uri=redirect_uri,
                client_id=self.auth.consumer.key,
                client_secret=self.auth.consumer.secret,
                **kwargs)

        if response.status != 200:
            raise Error('Error occured while exchanging code')
        return response

def create_request(url, client_id, client_secret, access_token=None, **kwargs):
    consumer = Consumer(client_id, client_secret)
    if access_token:
        token = Token(key=access_token)
    else:
        token = None

    request = www.Request(url, **kwargs)
    auth = consumer.Authority.Auth(consumer=consumer, token=token)
    request.processors.append(auth)
    return request

www.implement_methods(create_request, globals())
