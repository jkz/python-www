import functools
import mmap

from www import methods
from www import lib
from www.content import deserialize
from www.core import http
from www.utils.decorators import lazy_property
from www.utils.descriptors import BindablePartial

class Authority(http.Authority):
    """
    Requires the inheritor to have a domain string field.
    """
    host = None

    format = None
    streaming = False

    timeout = 5.0  # seconds
    reconnect_time = 5.0  #seconds
    exceptions = False

    auto_connect = True
    #auto_request = False

    headers = {} #TODO use the proper class

    processors = []  #XXX care, this is a mutable class property

    connection = None

    def __init__(self, url='', scheme=None, host=None, port=None, **kwargs):
        #XXX This needs to be synchronized with core.Authority
        super().__init__(
            host = url or host or self.host,
            port = port or self.port,
            scheme = scheme,
        )

        self.__dict__.update(kwargs)

    def __enter__(self):
        self.connect()

    def __exit__(self, type, value, traceback):
        self.disconnect()

    @property
    def connector(self):
        return lib.http.HTTPSConnection if self.secure else lib.http.HTTPConnection

    def connect(self):
        """
        Open the appropriate connection with the specified host.
        """
        if self.connection is not None:
            return
        self.connection = self.connector(host=self.host, port=self.port,
                timeout=self.timeout)

    def disconnect(self):
        """
        Close the connection if it is open.
        """
        if self.connection is None:
            return
        self.connection.close()
        self.connection = None

    def reconnect(self, reconnect_time=None):
        """
        Disconnect and then connect after sleeping passed or default seconds.
        """
        self.disconnect()
        if reconnect_time is None:
            reconnect_time = self.reconnect_time
        time.sleep(reconnect_time)
        self.connect()

    ######### http style requests

    def request(self, method, url, body=None, headers={}):
        """
        Issue a request on the connection. Open a connection if needed.
        """
        # Open a connection if it is not manually handled
        if self.auto_connect:
            self.connect()
        _headers = http.Header(self.headers or {})
        _headers.update(headers)

        params = method, url, body, _headers

        self.connection.request(*params)

    def getresponse(self, format=None):
        """
        Return a Response object, potentially in a predifined format.
        """
        _response = self.connection.getresponse()
        response = Response(_response, streaming=self.streaming, exceptions=self.exceptions)

        # Close the connection if it is not manually handled
        if self.auto_connect:
            self.disconnect()


        # Return parsed if format is specified
        format = format or self.format
        if format:
            return response.parse(format)

        return response

    #XXX: needs work on arguments
    def fetch(self, *args, **kwargs):
        format = kwargs.pop('format', None)
        self.request(*args, **kwargs)
        return self.getresponse(format=format)

    ######## www style requests

    def prepare(self, *args, **kwargs):
        """
        Return a request object.
        """
        kwargs['authority'] = self
        return Request(*args, **kwargs)

    def execute(self, *args, **kwargs):
        format = kwargs.pop('format', None)
        return self.prepare(*args, **kwargs).execute(format=format)


'''
for method in www.methods.ALL:
    def request(self, *args, **kwargs):
        kwargs['method'] = method
        return self.request(*args, **kwargs)
    request.__name__ = method.lower()
    setattr(Authority, method.lower(), request)
'''


def implement_methods(function, namespace, attr=False):
    """
    Insert curried versions of given function with each method to a namespace
    """
    #namespace['open'] = lambda url, **kwargs: function(url=url, **kwargs)()
    for method in methods.ALL:
        name = method.lower()
        #partial = functools.partial(function, method=method)
        partial = BindablePartial(function, method=method)
        if attr:
            setattr(namespace, name, partial)
        else:
            namespace[name] = partial

implement_methods(Authority.prepare, Authority, True)


class Resource(http.Resource):
    Authority = Authority

    def stream(self, method='GET', body=None, headers=None, **kwargs):
        return Request(resource=self, method=method, body=body,
                headers=headers).stream(**kwargs)

    def fetch(self, method='GET', body=None, headers=None, **kwargs):
        return Request(resource=self, method=method, body=body,
                headers=headers).fetch(**kwargs)


def add_user_agent(request):
    request.headers['User-Agent'] = request.headers.pop('User-Agent',
            USER_AGENT)

class Request(http.Request):
    Resource = Resource

    prepared = False

    def prepare(self):
        """Run all the processors on this request object"""
        if not self.prepared:
            return
        self.prepared = True

        for processor in self.processors:
            processor(self)

        add_user_agent(self)

    def split(self):
        self.prepare()
        return super().split()

    def stream(self, **kwargs):
        return self.url.authority.stream(*self.split(), **kwargs)

    def fetch(self):
        return self.url.authority.fetch(*self.split())

    '''
    def __call__(self, format=None):
        response = self.fetch(*self.params())
        if format:
            return response.parse(format)
        return response
    '''


class Response(http.Response):
    """
    Response from a callm request.
    Can represent data in different formats by calling the corresponding
    attribute.
    """
    #TODO: Behaviour is not optimal with streaming responses. Perhaps a read()
    #      wrapper should be added with a buffer and an index.
    #TODO: Encoding is not yet handled properly
    #TODO: return format equal to MIME-TYPE header
    #TODO: Handlers, like redirect, proxy etc
    #class Error(Error): pass
    #class ParseError(Error): pass

    def __init__(self, response, streaming=False, exceptions=False,
            redirects=False):
        super().__init__(
                code=response.status,
                reason=response.reason,
                headers=response.getheaders(),
                body=http.Body(iterable=response))

        self.version = response.version
        self.response = response

        if exceptions:
            if status >= 400:
                raise responses[status](response.read())

        if not streaming:
            self.raw = response.read()


    def __getattr__(self, attr):
        """
        Parameters missing on this class are requested from the http
        response object.
        """
        try:
            self.val = deserialize(self.utf8, attr)
        except AttributeError:
            #TODO Serialization error
            raise
        else:
            return self.val

    def read(self, *amt):
        return self.response.read(*amt)

    def readline(self, delimiter='\r\n'):
        """Return data read up to first occurrance of delimiter."""
        data = ''
        while not data.endswith(delimiter):
            data += self.read(1)
        # Exclude delimiter from return data
        return data[:-len(delimiter)]

    @lazy_property
    def raw(self):
        return self.read()

    @lazy_property
    def utf8(self):
        return self.raw.decode('utf8')

    def parse(self, type=None, **kwargs):
        """Do something smart to the data to discover its type"""
        if not type:
            type = self.headers['Content-Type']
        return deserialize(self.raw, type)

'''
class Pool:
    """
    This attribute allows
    """
    _pool = {}

    def __get__(self, obj, cls):
        return self._pool[obj.netloc] or None

    def __set__(self, obj, val):
        self._pool[obj.netloc] = val


class Http(Connection):
    connection = Pool()


class Https(Connection):
    connection = Pool()
    secure = True
'''
