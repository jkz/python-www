import callm
import authlib.oauth2 as oauth2

class Error(Exception): pass
class ParseError(Error): pass


class Auth(oauth2.Auth):
    def __call__(self, method, uri, body='', headers={}):
        """
        Add a token or id parameter to the query string.

        Heads up!

        Does not support duplicate keys.
        """

        resource = callm.Resource(uri)

        if self.token:
            resource.query['access_token'] = self.token.key
        elif self.consumer:
            resource.query['client_id'] = self.consumer.key

        return method, resource.uri, body, headers


class Provider(oauth2.Provider):
    secure = True
    host = 'graph.facebook.com'
    exchange_code_url = '/oauth/access_token'
    authenticate_uri = 'https://www.facebook.com/dialog/oauth'

    def exchange_code(self, code, redirect_uri):
        response = super(Provider, self).exchange_code(code, redirect_uri)
        try:
            return response.query
        except ValueError:
            error = response.json
            raise Error(error['type'] + error['message'])


class API(callm.Connection):
    secure = True
    host = 'graph.facebook.com'
    exchange_code_url = '/oauth/access_token'
    authenticate_uri = 'https://www.facebook.com/dialog/oauth'

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


class ConsumerInterface(oauth2.ConsumerInterface):
    API = API
    Auth = Auth
    Provider = Provider


class Consumer(oauth2.Consumer):
    API = API
    Auth = Auth
    Provider = Provider

class TokenInterface(oauth2.TokenInterface): pass
class Token(oauth2.Token): pass
