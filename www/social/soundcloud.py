import www
import www.auth import oauth2

class Error(www.Error): pass

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
            request.resource.query['oauth_token'] = self.token.key
        elif self.consumer:
            request.resource.query['client_id'] = self.consumer.key

class Authority(oauth2.Authority)
    AUTHENTICATE_URL = 'https://soundcloud.com/connect'
    EXCHANGE_CODE_URL = '/oauth2/token'

    class Connection(oauth2.Authority.Connection):
        secure = True
        host = 'api.soundcloud.com'

    def exchange_code(self, code, redirect_uri, grant_type='authorization_code'):
        creds = super().exchange_code(code, redirect_url,
                grant_type=grant_type).json

        if 'error' in creds:
            #TODO proper error class
            raise Exception(creds['error'])
        return creds

class API(oauth2.Service):
    class Connection(oauth2.Service.Connection):
        secure = True
        host = 'api.soundcloud.com'

        format = 'json'

    def me(self):
        return self.connection.GET('/me.json')

    def get_my_tracks(self):
        return self.connection.GET('/me/tracks.json')

    def get_my_own_activities(self):
        return self.connection.GET('/me/activities/all/own.json')

    def get_user(self, uid):
        return self.connection.GET('/users/%s.json' % uid)

    def get_user_tracks(self, uid):
        return self.connection.GET('/users/%s/tracks.json' % uid)

    def get_track(self, uid):
        return self.connection.GET('/tracks/%s.json' % uid)

