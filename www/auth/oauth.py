import time
import random
import hmac
import hashlib
import base64
import urllib.parse

import www
import www.auth

class Error(www.auth.Error):
    pass

def percent_encode(s):
    return urllib.parse.quote(str(s).encode('utf-8'), '~')

def percent_encode_dict(d):
    return {percent_encode(key) : percent_encode(val) for key, val in d.items()}

def normalize_url(url):
    resource = www.Resource(url)
    resource.fragment = None
    resource.query = None
    return resource.url

def build_base_string(method, url, parameter_string):
    # Prepare url by stripping fragments and query string
    base_url = normalize_url(url)
    return '&'.join((
            method.upper(),
            percent_encode(base_url),
            percent_encode(parameter_string)))

def build_header(header):
    return 'OAuth ' + ', '.join(('='.join
        ((percent_encode(k), '"{}"'.format(percent_encode(v))))
        for k, v in sorted(header.items())))

class Auth(www.auth.Auth):
    """
    An OAuth authorizer.
    """
    def set_token(self, oauth_token, oauth_token_secret):
        self.token = Token(key=oauth_token, secret=oauth_token_secret)

    def set_verifier(self, verifier):
        self.options['oauth_verifier'] = verifier

    @property
    def signing_key(self):
        key = percent_encode(self.consumer.secret) + '&'
        if self.token:
            key += percent_encode(self.token.secret)
        return key

    def signature(self, msg):
        """Builds a hmac_sha1 hash for the message."""
        key = self.signing_key.encode('ascii')
        raw = msg.encode('ascii')
        mac = hmac.new(key, raw, hashlib.sha1)
        dig = mac.digest()
        sig = base64.b64encode(dig)
        return sig.decode()

    def header(self, method, uri, **other_params):
        header = {}

        # Add the basic oauth paramters
        header['oauth_consumer_key'] = self.consumer.key
        header['oauth_signature_method'] = 'HMAC-SHA1'
        header['oauth_version'] = '1.0'
        header['oauth_timestamp'] = int(time.time())
        header['oauth_nonce'] = random.getrandbits(64)

        # Add token if we're authorizing a user
        if self.token:
            header['oauth_token'] = self.token.key

        # Override default header and add additional header params
        header.update(self.options)

        #XXX: Sorting should be done prior to encoding!
        #XXX: Is that so?

        # Prepare the parameter string for the base string
        params_dict = header.copy()
        params_dict.update(other_params)
        params_string = www.Query(sorted(params_dict.items()))

        # Build the base string from prepared parameter string
        base_string = build_base_string(method, uri, params_string)

        # Build the signature and add it to the parameters
        signature = self.signature(base_string)
        header['oauth_signature'] = signature

        # Return the constructed authorization header
        return build_header(header)

    def __call__(self, request):
        """
        Encode and sign a request according to OAuth 1.0 spec.

        Heads up!

        Does not support duplicate keys.
        """
        # Split the uri for the query string parameters
        params = {}
        params.update(request.resource.query)
        params.update(request.data)

        request.headers['Authorization'] = self.header(request.method,
                request.resource.absolute_path, **params)


#TODO: detailed error messages
#TODO: GET or POST?
class Authority(www.auth.Service):
    """
    Represents an authentication service.

    The constructor requires at least a `host` and an `auth` object
    """
    REQUEST_TOKEN_PATH = None
    ACCESS_TOKEN_PATH = None

    AUTHENTICATE_URL = None

    def get_request_token(self):
        response = self.POST(self.REQUEST_TOKEN_PATH)
        if response.status != 200:
            raise Error('Invalid response while obtaining request token.')
        return response.query

    def get_access_token(self, key, secret, verifier):
        self.auth.set_token(key, secret)
        self.auth.set_verifier(verifier)
        response = self.POST(self.ACCESS_TOKEN_PATH)
        if response.status != 200:
            raise Error('Invalid response while obtaining access token.')
        return response.query

    def get_authenticate_url(self, **kwargs):
        return www.URL(self.AUTHENTICATE_URL, **kwargs)


class Consumer(www.auth.Consumer):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret


class Token(www.auth.Token):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret



def create_request(url, consumer_key, consumer_secret, token_key=None,
        token_secret=None, **kwargs):

    consumer = Consumer(consumer_key, consumer_secret)

    if token_key:
        token = Token(token_key, token_secret)
    else:
        token = None

    request = www.Request(**kwargs)
    auth = consumer.Authority.Auth(consumer=consumer, token=token)
    request.processors.append(auth)
    return request

www.implement_methods(create_request, globals())
