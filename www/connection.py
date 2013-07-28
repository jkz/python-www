from www.core import Headers

class Connection:
    """
    Requires the inheritor to have a domain string field.
    """
    host = None
    secure = False

    format = None
    streaming = False

    port = None
    strict = False
    timeout = 5.0  # seconds
    reconnect_time = 5.0  #seconds
    exceptions = False

    auto_connect = True
    #auto_request = False

    headers = {} #TODO use the proper class

    processors = []  #XXX care, this is a mutable class property

    connection = None

    username = None
    password = None

    def __init__(self, host=None, **kwargs):
        if host:
            self.host = host
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __enter__(self):
        self.open()

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def netloc(self):
        if (self.port is not None
        and not (self.port == http.HTTP_PORT and self.scheme == 'http')
        and not (self.port == http.HTTPS_PORT and self.scheme == 'https')):
            host = ':'.join((self.host, str(self.port)))
        else:
            host = self.host

        if self.username is not None:
            if self.password is not None:
                user = ':'.join((self.username, self.password))
            else:
                user = self.username
            return '@'.join((user, host))

        return host

    @property
    def scheme(self):
        return 'https' if self.secure else 'http'

    def open(self):
        """
        Open the appropriate connection with the specified host.
        """
        # Return if the connection is opened already
        if self.connection is not None:
            return

        # Specify the connection type
        if self.secure:
            connector = http.HTTPSConnection
        else:
            connector = http.HTTPConnection

        # Open the connection
        self.connection = connector(host=self.host, port=self.port,
                strict=self.strict, timeout=self.timeout)


    def close(self):
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
        self.close()
        if reconnect_time is None:
            reconnect_time = self.reconnect_time
        time.sleep(reconnect_time)
        self.open()

    ######### http style requests

    def request(self, method, url, body=None, headers={}):
        """
        Issue a request on the connection. Open a connection if needed.
        """
        # Open a connection if it is not manually handled
        if self.auto_connect:
            self.open()
        _headers = Header(self.headers or {})
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
            self.close()


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
        kwargs['connection'] = self
        return Request(*args, **kwargs)

    def execute(self, *args, **kwargs):
        format = kwargs.pop('format', None)
        return self.prepare(*args, **kwargs).execute(format=format)


for method in www.methods.ALL:
    def request(self, *args, **kwargs):
        kwargs['method'] = method
        return self.request(*args, **kwargs)
    request.__name__ = method.lower()
    setattr(Connection, method.lower(), request)


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


# Namespace api
def implement_methods(function, namespace):
    """
    Adds `open` and lowercased versions of each method to the namespace,
    to invoke request objects created by given function.
    """
    namespace['open'] = lambda url, **kwargs: function(url=url, **kwargs)()

    for method in methods.ALL:
        namespace[method.lower()] = functools.partial(namespace['open'], method=method)


def create_request(url, **kwargs):
    return Request(url=url, **kwargs)

implement_methods(create_request, globals())

if __name__ == "__main__":
    import doctest
    doctest.testmod()


