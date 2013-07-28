import mmap
import collections
import io

import www

from www import methods
from www import lib
from www.utils import structures
from . import exceptions

class Method:
    def __init__(self, verb=None, allowed=methods.ALL):
        self.allowed = allowed
        self.verb = self.convert(verb)

    def convert(self, verb):
        if verb is not None:
            verb = verb.upper()
            if self.allowed is not None and verb not in self.allowed:
                raise exceptions.MethodNotAllowed(verb)
        return verb

    def __set__(self, instance, verb):
        self.verb = self.convert(verb)

    def __get__(self, instance, owner):
        return self.verb


class Meta(dict):
    pass

class Query(structures.MultiDict):
    def __init__(self, *args, verbatim=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_verbatim = verbatim

    def verbatim(self):
        return '&'.join(('='.join(map(str, p)) for p in self.items(multi=True)))

    def encoded(self):
        return lib.urlencode(list(self.items(multi=True)))

    def __str__(self):
        if self.use_verbatim:
            return self.verbatim()
        else:
            return self.encoded()

class Port:
    def __init__(self, port=None):
        self.port = port

    def __get__(self, obj, cls):
        if self.port is not None:
            return self.port
        elif obj.secure:
            return 443
        else:
            return 80

    def __set__(self, obj, val):
        self.port = int(val or 0) or None


class Authority:
    port = Port()

    def __init__(self,
            url='',
            scheme=None,
            host=None,
            port=None,
            #username=None,
            #password=None,
        ):

        # Split the url into scheme, port, host, query and path
        _scheme, netloc, _, _, _ = lib.urlsplit(url, True)

        # Set the connection on self to extract parameters and enable requests.
        # split the netlocation into userinfo and hostinfo
        userinfo, _, hostinfo = netloc.rpartition('@')

        #_username, _, _password = userinfo.partition(':')

        _host, _, _port = hostinfo.partition(':')

        self.scheme = scheme or _scheme or 'http'
        self.host = host or _host
        #XXX automatic port for default schemes could be desirable
        self.port = port or _port
        #self.username = username or _username or None
        #self.password = password or _password or None

    @property
    def secure(self):
        return self.scheme == 'https'

    @property
    def userinfo(self):
        return None
        # Disabled for now

        if self.username is None:
            return

        if self.password is None:
            return self.username

        return '{}:{}'.format(self.username, self.password)

    @property
    def server(self):
        if (self.port
        and not (self.port == 80 and self.scheme == 'http')
        and not (self.port == 443 and self.scheme == 'https')):
            return '{}:{}'.format(self.host, self.port)

        return self.host

    def split(self):
        return (self.scheme, self.server, '', '', '')

    def __str__(self):
        return lib.urlunsplit(self.split())



class Resource:
    """
    A flexible url builder class. Deconstructs a given url into parts, then
    sets or replaces parts by explicitly passed parts.

    Usage example:

    >>> Resource('//example.com/foo?kitten=cake', host='otherhost.net',
    ...         kitten='fluffy').url
    'http://otherhost.net/foo?kitten=fluffy'
    """
    #XXX: A normalize method would be nice
    #TODO: encoding check
    def __init__(self,
            url=None,

            authority=None,

            scheme=None,
            host=None,
            port=None,
            #username=None,
            #password=None,

            path=None,
            query=None,
            query_string=None,
            fragment=None,
            verbatim=False,
            **kwargs
    ):
        url = url or ''

        # Split the url into scheme, port, host, query and path
        _scheme, netloc, self.path, _query_string, self.fragment = lib.urlsplit(url, True)

        # Create a netlocation object
        self.authority = authority or Authority(netloc,
                scheme=_scheme or scheme, host=host, port=port)

        # Override path if explicitly passed
        if path is not None:
            self.path = path

        # Override fragment if explicitly passed
        if fragment is not None:
            self.fragment = fragment

        # Create the query dictionary, flag wether to encode parameters
        # verbatim
        self.query = Query(verbatim=verbatim)
        # Populate it from parameters with following precedence (least first):
        # 1. `url`
        if _query_string is not None:
            self.query.update(lib.parse_qsl(_query_string))
        # 2. `query_string`
        if query_string is not None:
            self.query.update(lib.parse_qsl(query_string))
        # 3. `query`
        if query is not None:
            self.query.update(query)
        # 4. `kwargs
        self.query.update(kwargs)

    @property
    def query_string(self):
        return str(self.query)

    def split(self):
        return (self.authority.scheme, self.authority.server, self.path,
                self.query_string, self.fragment)

    @property
    def identifier(self):
        """
        Return absolute path, the url string without scheme and netloc parts
        """
        return lib.urlunsplit(('', '', self.path, self.query_string, self.fragment))

    @property
    def url(self):
        return lib.urlunsplit(self.split())

    def __str__(self):
        """
        Return a string containing the complete url.
        """
        return self.url


class Header(structures.MultiDict):
    def __str__(self):
        return '\n'.join('{}: {}'.format(key, ','.join(map(str, vals))) for key, vals in self.listvalues())


class Body:
    """
    An interface to all kinds of request bodies.
    """
    def __init__(self, body=None, fileno=None):
        if body:
            self.body = body
        elif fileno:
            self.map = mmap.mmap(fileno(), 0, prot=mmap.PROT_READ)
        else:
            self.body = io.StringIO()

    def read(self, size):
        return self.body.read()

    def readline(self):
        return self.body.readline()

    def readlines(self, hint):
        if self.body:
            return self.body.readlines(hint)

        if self.map:
            for line in iter(self.map.readline, hint):
                yield line

    def __iter__(self):
        return self.body.__iter__()

    def __str__(self):
        return str(self.body)


class ErrorStream:
    def flush(self):
        pass

    def write(self, str):
        pass

    def writelines(self, seq):
        pass


class Request(collections.UserDict):
    class Error(exceptions.Error): pass

    method = Method()

    def __init__(
            self,
            url = '',
            method = None,
            body = None,
            headers = None,
            meta = None,
            resource = None,
            **kwargs
    ):
        # (. )( .)! Not all named arguments are passed to the Resource.
        self.resource = resource or Resource(url, **kwargs)
        self.method = method or 'GET'
        self.headers = Header(headers or {})
        self.body = body  #Body(body)
        self.meta = Meta(meta or {})

        super().__init__()

    def split(self):
        method = self.method
        url = self.resource.identifier
        body = self.body
        headers = self.headers.copy()
        return (method, url, body, headers)

    def __str__(self):
        return '{} {}'.format(self.method, self.resource)


class Response:
    def __init__(self,
            status,
            reason=None,
            headers=None,
            body=None,
    ):
        self.status = status
        self.reason = reason
        self.headers = Header(headers or {})
        self.body = Body(body)
