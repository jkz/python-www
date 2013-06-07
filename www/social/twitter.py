import functools
import www
from www.auth import oauth
from www.utils import default_kwargs


#TODO Streams!

class Consumer(oauth.Consumer):
    Provider = None

class Token(oauth.Token): pass

class Authority(oauth.Authority):
    AUTHENTICATE_URL = 'http://twitter.com/oauth/authenticate'

    REQUEST_TOKEN_PATH = '/oauth/request_token'
    ACCESS_TOKEN_PATH = '/oauth/access_token'

    class Connection(www.Connection):
        host = 'api.twitter.com'


class Error(Exception): pass

class API(oauth.Service):
    class Connection(oauth.Service.Connection):
        host = 'api.twitter.com'
        secure = True

        format = 'json'

    @default_kwargs(
            include_my_retweet='true',
            include_entities='true')
    def get_status(self, uid, **kwargs):
        return self.GET('/1/statuses/show.json', id=uid, **kwargs)

    @default_kwargs(
            include_entities='true')
    def get_user(self, uid, **params):
        try:
            int(uid)
        except ValueError:
            params['screen_name'] = uid
        else:
            params['user_id'] = uid
        return self.GET('/1/users/show.json', **params)

    @default_kwargs(
            trim_user=True,
            exclude_replies=True,
            contributor_details=False,
            include_rts=True)
    def get_timeline(self, uid, max_id=None, since_id=None, **params):
        try:
            int(uid)
        except ValueError:
            params['screen_name'] = uid
        else:
            params['user_id'] = uid
        if max_id is not None:
            params['max_id'] = max_id
        if since_id is not None:
            params['since_id'] = since_id
        return self.GET('/1.1/statuses/user_timeline.json', **params)


class Stream(www.Stream):
    secure = True
    snooze_time = 5.0

    _delimiter = 'length'

    def __init__(self, auth, listener=None):
        super(Stream, self).__init__(auth=auth, listener=listener)

    def read_loop_iter(self):
        # Note: keep-alive newlines might be inserted before each length value.
        # read the delimiter string
        delimited_string = self.readline()

        # return the next payload
        if delimited_string.isdigit():
            byte_count = int(delimited_string)
            ret = self.read(byte_count)
            return ret
        #XXX we actually don't want this to happen
        else:
            return delimited_string
        return None

    def retry_time(self, error_count):
        return {
            0: 0.0, # Should not occur
            1: 10.0,
            2: 20.0,
            3: 40.0,
            4: 80.0,
            5: 160.0
        }.get(error_count, 240.0)


def encode_list_params(*list_names):
    """',' joins all params lists whose key is present in given name_list"""
    def decorator(func):
        @functools.wraps(func)
        def funk(*args, **params):
            for key in list_names:
                val = params.get(key, None)
                if val is not None:
                    params[key] = ','.join(map(str, val))
            return func(*args, **params)
        return funk
    return decorator


class StatusStream(Stream):
    host = 'stream.twitter.com'

    @default_kwargs(
            count=0,
            delimited='length',
            stall_warning='true')
    @encode_list_params('track', 'locations', 'follow')
    def filter(self, **params):
        params['headers'] = {'Content-Type': 'application/x-www-form-urlencoded'}
        return self.POST('/1.1/statuses/filter.json', **params)

    @default_kwargs(
            count=0,
            delimited='length',
            stall_warning='true')
    def firehose(self, **params):
        return self.GET('/1/statuses/firehose.json', **params)

    @default_kwargs(
            count=0,
            delimited='length',
            stall_warning='true')
    def links(self, **params):
        return self.GET('/1/statuses/links.json', **params)

    @default_kwargs(
            delimited='length',
            stall_warning='true')
    def retweet(self, **params):
        return self.GET('/1/statuses/retweet.json', **params)

    @default_kwargs(
            count=0,
            delimited='length',
            stall_warning='true')
    def sample(self, **params):
        return self.GET('/1/statuses/sample.json', **params)


class UserStream(Stream):
    host = 'userstream.twitter.com'

    @default_kwargs(**{
            'count': 0,
            'delimited': 'length',
            'stall_warning': 'true',
            'with': 'followings'}) # use 'user' for user related only
    def __call__(self, **params):
        return self.GET('/2/user.json', **params)


class SiteStream(Stream):
    host = 'sitestream.twitter.com'

    @default_kwargs(**{
            'count': 0,
            'delimited': 'length',
            'stall_warning': 'true',
            'with': 'followings'}) # use 'user' for user related only
    @encode_list_params('follow',)
    def __call__(self, **params):
        return self.stream.GET('/2b/site.json', **params)

