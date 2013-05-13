import www
from www.auth import oauth
from www.utils import default_kwargs

class Error(www.Error): pass

class Consumer(oauth.Consumer): pass
class Token(oauth.Token): pass

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


class Authority(oauth.Authority):
    class Connection(oauth.Authority.Connection):
        host = 'www.tumblr.com'
        request_token_path = '/oauth/request_token'
        access_token_path = '/oauth/access_token'
        authorize_uri = 'http://www.tumblr.com/oauth/authorize'


def blogname(name):
    if not name.count('.'):
        name += '.tumblr.com'
    return name

class Authority(oauth.Service):
    class Connection(oauth.Service.Connection):
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
        return self.connection.GET('/v2/blog/%s/posts%s' % (blogname(blog),
            type and '/' + type or ''), **kwargs).json


    def get_post(self, blog, uid, **kwargs):
        return self.get_posts(blog, id=uid, **kwargs)

    def get_user(self):
        return self.connection.GET('/v2/user/info').json

    def get_blog(self, blog):
        return self.connection.GET('/v2/blog/%s/info' % blogname(blog)).json

    def get_tagged(self, tag):
        return self.connection.GET('/v2/tagged', tag=tag).json

