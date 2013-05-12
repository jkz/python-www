import www
from www.auth import oauth

class Error(www.Error):
    pass

class Auth(oauth.Auth):
    def __call__(self, request):
        path = request.resource.path
        if (path.startswith('/v2/tagged')
        or path.startswith('/v2/blog/')
        and ((path.endswith('/info')
            or path.endswith('/likes')
            or path.endswith('/posts')
            or path.endswith('/posts/text')
            or path.endswith('/posts/photo')))):
                request.resource.query['api_key'] = self.consumer.key
        else:
            super(Auth, self).__call__(request)


class Provider(oauth.Provider):
    secure = True
    host = 'api.linkedin.com'
    request_token_path = '/uas/oauth/requestToken'
    access_token_path = '/uas/oauth/accessToken'
    authorize_uri = 'https://www.linkedin.com/uas/oauth/authenticate'


class API(www.Connection):
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


class Consumer(oauth.Consumer): pass
class Token(oauth.Token): pass
