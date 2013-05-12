import callm
import authlib.oauth as oauth

class Error(Exception):
    pass

class Auth(oauth.Auth):
    def __call__(self, method, uri, body='', headers={}):
        resource = callm.Resource(uri)
        path = resource.path
        if (path.startswith('/v2/tagged')
        or path.startswith('/v2/blog/')
        and ((path.endswith('/info')
            or path.endswith('/likes')
            or path.endswith('/posts')
            or path.endswith('/posts/text')
            or path.endswith('/posts/photo')))):
                resource.query['api_key'] = self.consumer.key
                return method, resource.uri, body, headers
        return super(Auth, self).__call__(method, uri, body, headers)


class Provider(oauth.Provider):
    secure = True
    host = 'api.linkedin.com'
    request_token_path = '/uas/oauth/requestToken'
    access_token_path = '/uas/oauth/accessToken'
    authorize_uri = 'https://www.linkedin.com/uas/oauth/authenticate'


class API(callm.Connection):
    secure = True
    host = 'api.linkedin.com'

    @property
    def _GET(self):
        headers = {'x-li-format': 'json'}
        return self.suspend.GET('/v1', headers=headers)

    def get_profile(self, uid=None, url=None):
        fields = ['id', 'first-name', 'last-name', 'headline', 'picture-url']
                #'site-standard-profile-request',
                #'api-standard-profile-request']
        if uid:
            tail = 'id=' + uid
        elif url:
            tail = 'url=' + url
        else:
            tail = '~'
        field_selector = ''.join((':(', ','.join(fields), ')'))
        path = ''.join(('/v1/people/', tail, field_selector))
        headers = {'x-li-format': 'json'}
        return self.GET(path, headers=headers).json


class ConsumerInterface(oauth.ConsumerInterface):
    Auth = Auth
    API = API
    Provider = Provider


class Consumer(oauth.Consumer):
    Auth = Auth
    API = API
    Provider = Provider

class TokenInterface(oauth.TokenInterface): pass
class Token(oauth.Token): pass
