"""
Last.fm (Authentication) API

This is Version 1.0 of the Last.fm authentication API specification.

http://www.last.fm/ap/webauth
"""
import callm
import hashlib

from authlib import interface

class Error(Exception):
    '''
    errors = {
        2 : INVALID_SERVICE
        3 : INVALID_METHOD
        4 : AUTHENTICATION_FAILED
        5 : INVALID_FORMAT
        6 : INVALID_PARAMETERS
        7 : INVALIED_RESOURCE
        8 : OPERATION_FAILED
        9 : INVALID_SESSION_KEY
        10 : INVALID_API KEY
        11 : SERVICE_OFFLINE
        13 : INVALID_SIGNATURE
        16 : TEMPORARY_ERROR
        26 : SUSPENDED_API_KEY
        29 : RATE_LIMIT_EXCEEDED
    }

    {
    '2' : INVALID_SERVICE - This service does not exist
    '3' : INVALID_METHOD - No method with that name in this package
    '4' : AUTHENTICATION_FAILED - You do not have permissions to access the service
    '5' : INVALID_FORMAT - This service doesn't exist in that format
    '6' : INVALID_PARAMETERS - Your request is missing a required parameter
    '7' : INVALIED_RESOURCE = Invalid resource specified
    '8' : OPERATION_FAILED - Something else went wrong
    '9' : INVALID_SESSION KEY - Please re-authenticate
    10' : INVALID_API KEY - You must be granted a valid key by last.fm
    11' : SERVICE_OFFLINE - This service is temporarily offline. Try again later.
    '13' : Invalid method signature supplied
    '16' : There was a temporary error processing your request. Please try again
    '26' : SUSPENDED_API_KEY - Access for your account has been suspended, please
    contact Last.fm
    '29' : RATE_LIMIT_EXCEEDED - Your IP has made too many requests in a short period
    }

    '''
    pass

class Auth(interface.Auth):
    def __init__(self, consumer, token=None, **options):
        self.consumer = consumer
        self.token = token
        self.options = options

    def __call__(self, method, uri, body='', headers={}):
        """
        5. Make authenticated web service calls
        You can now sign your web service calls with a method signature,
        provided along with the session key you received in Section 4 and your
        API key. You will need to include all three as parameters in subsequent
        calls in order to be able to access services that require
        authentication. You can visit individual method call pages to find out
        if they require authentication. Your three authentication parameters
        are defined as:

            sk (Required) : The session key returned by auth.getSession service.
            api_key (Required) : Your 32-character API key.
            api_sig (Required) : Your API method signature, constructed as
                explained in Section 6
        """
        resource = callm.Resource(uri)
        resource.query['api_key'] = self.consumer.key
        if self.token:
            resource.query['sk'] = self.token.key
        resource.query.update(self.options)
        resource.query['api_sig'] = self.signature(**resource.query)
        uri = resource.uri
        return method, resource.uri, body, headers

    def signature(self, **query):
        """
        6. Sign your calls
        Construct your api method signatures by first ordering all the
        parameters sent in your call alphabetically by parameter name and
        concatenating them into one string using a <name><value> scheme. So for
        a call to auth.getSession you may have:

            api_keyxxxxxxxxmethodauth.getSessiontokenxxxxxxx

        Ensure your parameters are utf8 encoded. Now append your secret to
        this string. Finally, generate an md5 hash of the resulting string.
        For example, for an account with a secret equal to 'mysecret', your
        api signature will be:

            api signature = md5("api_keyxxxxxxxxmethodauth.getSessiontokenxxxxxxxmysecret")

        Where md5() is an md5 hashing operation and its argument is the
        string to be hashed. The hashing operation should return a
        32-character hexadecimal md5 hash.
        """
        param = ''.join('%s%s' % (k, v) for k, v in sorted(query.iteritems()))
        param += self.consumer.secret
        param = param.encode('utf-8')
        md5 = hashlib.md5()
        md5.update(param)
        return md5.hexdigest()

class API(callm.Connection):
    host = 'ws.audioscrobbler.com'
    secure = False
#    format = 'json'

    auth_uri = 'http://www.last.fm/api/auth/'

    def auth_request(self, redirect_uri, **kwargs):
        """
        2. Request authorization from the user
        Send your user to last.fm/api/auth with your API key as a parameter.
        Use an HTTP GET request. Your request will look like this:

            http://www.last.fm/api/auth/?api_key=xxx

        If the user is not logged in to Last.fm, they will be redirected to
        the login page before being asked to grant your web application
        permission to use their account. On this page they will see the
        name of your application, along with the application description
        and logo as supplied in Section 1.

        2.1 Custom callback url
        You can optionally specify a callback URL that is different to your
        API Account callback url. Include this as a query param cb. This
        allows you to have users forward to a specific part of your site
        after the authorisation process.

            http://www.last.fm/api/auth/?api_key=xxx&cb=http://example.com
        """
        return callm.URL(self.auth_uri, verbatim=False,
                api_key=self.auth.consumer.key, cb=redirect_uri, **kwargs)

    def auth_callback(self, token, **kwargs):
        """
        3. Create an authentication handler
        ---------
        Once the user has granted permission to use their account on the
        Last.fm page, Last.fm will redirect to your callback url, supplying an
        authentication token as a GET variable.

        <callback_url>/?token=xxxxxxx

        If the callback url already contains a query string then token variable
        will be appended, like;

        <callback_url>&token=xxxxxxx

        The script located at your callback url should pick up this
        authentication token and use it to create a Last.fm web service session
        as described in Section 4.

        3.1 Authentication Tokens
        Authentication tokens are user and API account specific.
        They are valid for 60 minutes from the moment they are granted.
        """
        xml = self.get_session(token, **kwargs).xml
        key = xml.getElementsByTagName('key')[0].firstChild.data
        return {'key': key}

    def get_session(self, token, **kwargs):
        """
        4. Fetch a Web Service Session
        ---------
        Send your api key along with an api signature and your authentication
        token as arguments to the auth.getSession API method call. The
        parameters for this call are defined as such:

        api_key: Your 32-character API Key.
        token: The authentication token received at your callback url as a GET
        variable.
        api_sig: Your 32-character API method signature, as explained in
        Section 6

        Note: You can only use an authentication token once. It will be
        consumed when creating your web service session.
        The response format of this call is shown on the auth.getSession method
        page.

        Section Session Lifetime
        Session keys have an infinite lifetime by default. You are recommended
        to store the key securely. Users are able to revoke privileges for your
        application on their Last.fm settings screen, rendering session keys
        invalid.
        """
        return self.GET('/2.0/', method='auth.getSession', token=token, **kwargs)


    def get_user(self, user=None, **params):
        """
        Params
        user (Optional) : The user to fetch info for. Defaults to the
        authenticated user.
        """
        if user:
            params['user'] = user
        return self.GET('/2.0/', method='user.getInfo', format='json', **params).json

    def get_artist(self, artist, **params):
        """
        artist (Required (unless mbid)] : The artist name
        mbid (Optional) : The musicbrainz id for the artist
        lang (Optional) : The language to return the biography in, expressed as an ISO 639 alpha-2 code.
        autocorrect[0|1] (Optional) : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response.
        username (Optional) : The username for the context of the request. If supplied, the user's playcount for this artist is included in the response.
        api_key (Required) : A Last.fm API key.
        """
        if not 'username' in params and self.auth.token:
            params['username'] = self.auth.token.user.name
        return self.GET('/2.0/', method='artist.getInfo', format='json',
               artist=artist, **params).json

    def get_library(self, artist=None, album=None, **params):
        if not 'user' in params and self.auth.token:
            params['user'] = self.auth.token.user.name
        if artist:
            params['artist'] = artist
        if album:
            params['album'] = album
        return self.GET('/2.0/', method='library.getTracks', format='json', **params).json

    def get_track(self, artist, track, **params):
        """
        mbid (Optional) : The musicbrainz id for the track
        track (Required (unless mbid)] : The track name
        artist (Required (unless mbid)] : The artist name
        username (Optional) : The username for the context of the request. If
        supplied, the user's playcount for this track and whether they have
        loved the track is included in the response.
        autocorrect[0|1] (Optional) : Transform misspelled artist and track
        names into correct artist and track names, returning the correct
        version instead. The corrected artist and track name will be returned
        in the response.
        """
        if not 'username' in params and self.auth.token:
            params['username'] = self.auth.token.user.name
        return self.GET('/2.0/', method='track.getInfo', format='json',
                track=track, artist=artist, **params).json


class ConsumerInterface(interface.Consumer):
    key = None
    secret = None

    Provider = API = API
    Auth = Auth

    def auth_process(self, session_token):
        """
        Return a user object
        """
        raise NotImplementedError

    def __unicode__(self):
        return 'lastfm.App(%s)' % self.key


class TokenInterface(interface.Token):
    key = None
    consumer = None


class Consumer(ConsumerInterface):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret


class Token(TokenInterface):
    def __init__(self, key, consumer=None):
        self.key = key
        self.consumer = consumer

