import callm
import authlib.oauth as oauth

#TODO utils is still an app
from utils.decorators import default_kwargs

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
    host = 'www.tumblr.com'
    request_token_path = '/oauth/request_token'
    access_token_path = '/oauth/access_token'
    authorize_uri = 'http://www.tumblr.com/oauth/authorize'


def blogname(name):
    if not name.count('.'):
        name += '.tumblr.com'
    return name

class API(callm.Connection):
    host = 'api.tumblr.com'
    secure = False

    # blog names can be either standard:
    #
    #    my_name.tumblr.com
    #
    # or:
    #
    #    any.thing.com
    #
    @default_kwargs(
            reblog_info='false',
            notes_info='false',
            limit=20,
            offset=0)
    def get_posts(self, blog, type=None, **kwargs):
        return self.GET('/v2/blog/%s/posts%s' % (blogname(blog),
            type and '/' + type or ''), **kwargs).json


    def get_post(self, blog, uid, **kwargs):
        return self.get_posts(blog, id=uid, **kwargs)

    def get_user(self):
        return self.GET('/v2/user/info').json

    def get_blog(self, blog):
        return self.GET('/v2/blog/%s/info' % blogname(blog)).json

    def get_tagged(self, tag):
        return self.GET('/v2/tagged', tag=tag).json


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
