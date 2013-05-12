import www
import www.auth

class Error(www.auth.Error):
    pass


class Auth(www.auth.Auth):
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
            request.resource.query['client_id'] = self.token.key


class Service(www.auth.Service):
    EXCHANGE_CODE_URL = None

    def request_code(self, redirect_uri, **kwargs):
        """Return a redirect url"""
        query = dict(client_id=self.auth.consumer.key, redirect_uri=redirect_uri)
        query.update(kwargs)
        return www.URL(self.provider.authenticate_uri, verbatim=False, **query)

    def exchange_code(self, code, redirect_uri, **kwargs):
        """
        Trade a code for access credentials. They are returned as a
        www.Response object, to be parsed by the caller.
        """
        response = self.provider.POST(
                self.EXCHANGE_CODE_URL,
                code=code,
                redirect_uri=redirect_uri,
                client_id=self.auth.consumer.key,
                client_secret=self.auth.consumer.secret,
                **kwargs)

        if response.status != 200:
            raise Error('Error occured while exchanging code')
        return response


class Consumer(www.auth.Consumer):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def __str__(self):
        return 'oauth_consumer(%s)' % self.key


class Token(www.auth.Token):
    def __init__(self, consumer, key):
        self.consumer = consumer
        self.key = key


