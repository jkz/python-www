import www

from www.auth as auth
from www.auth import oauth2

class Error(www.Exception): pass
class ParseError(Error): pass

class Consumer(oauth2.Consumer): pass
class Token(oauth2.Token): pass

class Auth(auth.Auth):
    def __call__(self, request):
        """
        Add a token or id parameter to the query string.

        Heads up!

        Does not support duplicate keys.
        """
        if self.token:
            request.headers['Authorization'] = 'Bearer %s' % self.token.key


class Provider(oauth2.Provider):
    host = 'accounts.google.com'
    secure = True
    authenticate_uri = 'https://accounts.google.com/o/oauth2/auth'
    exchange_code_url = '/o/oauth2/token'

    def request_code(self, redirect_uri, scope=None, access_type='offline',
            state=None, approval_prompt='auto'):
        params = {}
        if state is not None:
            params['state'] = state
        if scope is None:
            scope = 'https://www.googleapis.com/auth/youtube'
        return super(Provider, self).request_code(
                redirect_uri,
                response_type='code',
                scope=scope,
                access_type=access_type,
                approval_prompt=approval_prompt,
                **params)

    def exchange_code(self, code, redirect_uri):
        response = super(Provider, self).exchange_code(code, redirect_uri,
                grant_type='authorization_code')
        try:
            return response.query
        except ValueError:
            error = response.json
            raise Error(error['type'] + error['message'])


class API(www.Connection):
    host = 'www.googleapis.com'
    secure = True
    authenticate_uri = 'https://www.facebook.com/dialog/oauth'

    format = 'json'

    def GET(self, path, **options):
        return super(API, self).GET('/youtube/v3' + path, **options)

    def get_channel(self, uid, part=None, **options):
        if part is None:
            part = 'id', 'snippet', 'contentDetails', 'statistics', 'topicDetails'
        if isinstance(part, (list, tuple)):
            part = ','.join(part)

        return self.GET('/channels', id=uid, part=part, **options)

    def get_video(self, uid, part=None):
        if part is None:
            part = 'id', 'snippet', 'contentDetails', 'status', 'statistics', 'topicDetails'
        if isinstance(part, (list, tuple)):
            part = ','.join(part)

        return self.GET('/videos', id=uid, part=part)

