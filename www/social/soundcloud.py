import callm
import authlib.oauth2 as oauth2

class Error(Exception):
    pass


class Auth(oauth2.Auth):
    def __call__(self, method, uri, body='', headers={}):
        """
        Add a token or id parameter to the query string.

        Heads up!

        Does not support duplicate keys.
        """

        resource = callm.Resource(uri)

        if self.token:
            resource.query['oauth_token'] = self.token.key
        elif self.consumer:
            resource.query['client_id'] = self.consumer.key

        return method, resource.uri, body, headers

class Provider(oauth2.Provider):
    secure = True
    host = 'api.soundcloud.com'
    exchange_code_url = '/oauth2/token'
    authenticate_uri = 'https://soundcloud.com/connect'


    #XXX: This could be accomplishable by a 'format' attribute
    #format = 'json'
    def exchange_code(self, code, redirect_uri, grant_type):
        return super(Provider, self).exchange_code(code, redirect_uri,
                grant_type=grant_type).json


class API(callm.Connection):
    secure = True
    host = 'api.soundcloud.com'

    format = 'json'

    def me(self):
        return self.GET('/me.json')

    def get_my_tracks(self):
        return self.GET('/me/tracks.json')

    def get_my_own_activities(self):
        return self.GET('/me/activities/all/own.json')

    def get_user(self, uid):
        return self.GET('/users/%s.json' % uid)

    def get_user_tracks(self, uid):
        return self.GET('/users/%s/tracks.json' % uid)

    def get_track(self, uid):
        return self.GET('/tracks/%s.json' % uid)


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
