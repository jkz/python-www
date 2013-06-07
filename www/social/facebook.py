from www.auth import oauth2

class Error(Exception): pass
class ParseError(Error): pass

class Consumer(oauth2.Consumer): pass
class Token(oauth2.Token): pass

class Auth(oauth2.Auth):
    def __call__(self, request):
        """
        Add a token or id parameter to the query string.

        Heads up!

        Does not support duplicate keys.
        """
        if self.token:
            request.resource.query['access_token'] = self.token.key
        elif self.consumer:
            request.resource.query['client_id'] = self.consumer.key


class Authority(oauth2.Authority):
    AUTHENTICATE_URL = 'https://www.facebook.com/dialog/oauth'
    EXCHANGE_CODE_URL = '/oauth/access_token'

    class Connection(oauth2.Authority.Connection):
        secure = True
        host = 'graph.facebook.com'

    def exchange_code(self, code, redirect_uri):
        response = super(Authority, self).exchange_code(code, redirect_uri)
        try:
            return response.query
        except ValueError:
            error = response.json
            raise Error(error['type'] + error['message'])


class API(oauth2.Service):
    class Connection(oauth2.Service.Connection):
        secure = True
        host = 'graph.facebook.com'

    def get_obj(self, uid, **options):
        return self.GET(uid, **options).json

    def get_status(self, uid):
        return self.get_obj(uid)

    def get_user(self, uid):
        fields = ['id', 'name', 'first_name', 'last_name', 'link', 'username',
                'gender', 'timezone', 'verified']
        return self.GET(uid, fields=fields).json

    def me(self):
        return self.get_user('me')

