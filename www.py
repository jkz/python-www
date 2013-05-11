"""
A sexy urllib and http wrapper for Python 3.

DOES NOT SUPPORT DUPLICATE KEYS.

Contents:
    Error
    HTTPError

    Resource
    URL
    AbsolutePath
    Query
    Request
    Response
    Connection
    Stream
    Listener
"""

import urllib.parse
import http.client
import collections

import json
import xml.dom.minidom
import functools
import time
import socket
import threading

NAME = 'www'
VERSION = '0.0.1'
USER_AGENT = '{}/{}'.format(NAME, VERSION)

METHODS = 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS'

class Error(Exception): pass
class HTTPException(Error, http.client.HTTPException): pass

# This creates an exception class for each http response status.
# The responses dict has their codes as keys, the global namespace has
# their constant names from http.client camelcased.
# e.g. NOT_FOUND becomes NotFound
responses = {}
for code, name in http.client.responses.items():
    name = name.replace(' ', '')
    class Status(HTTPException):
        code = code
    Status.__name__ = name
    globals()[name] = responses[code] = Status


class Query(str):
    """
    A querystring builder class.

    Turns keyword arguments into a urlencoded querystring.

    query -- a dictionary or sequence of pair tuples
    verbatim -- turns off urlencoding when True
    """
    def __new__(self, query=(), verbatim=False, **kwargs):
        pairs = []
        try:
            pairs.extend(query.items())
        except AttributeError:
            pairs.extend(query)
        pairs.extend(kwargs.items())
        if verbatim:
            return '&'.join(('='.join(map(str, p)) for p in pairs))
        else:
            return urllib.parse.urlencode(pairs)


class Resource:
    """
    A flexible url builder class. Deconstructs a given url into parts, then
    sets or replaces parts by explicitly passed parts.

    Usage example:

    >>> Resource('//example.com/foo?kitten=cake', host='otherhost.net',
    ...         kitten='fluffy', secure=True).url
    'https://otherhost.net/foo?kitten=fluffy'
    """
    #XXX: A normalize method would be nice
    #TODO: encoding check
    def __init__(self,
            url='',
            connection=None,
            scheme=None,
            host=None,
            port=None,
            path=None,
            query=None,
            query_string=None,
            fragment=None,
            secure=None,
            username=None,
            password=None,
            verbatim=False,
            **kwargs
    ):
        # Determines whether parameters are combined encoded or verbatim
        self.verbatim = verbatim

        # Split the url into scheme, port, host, query and path
        _scheme, _netloc, self.path, _query_string, self.fragment = urllib.parse.urlsplit(url)

        # Set the connection on self to extract parameters and enable requests.
        if connection:
            self.connection = connection
        else:
            # split the netlocation into userinfo and hostinfo
            userinfo, _, hostinfo = _netloc.rpartition('@')

            # extract the username and password
            _username, _, _password = userinfo.partition(':')

            _host, _, _port = _netloc.partition(':')

            self.connection = Connection(
                host     = host or _host or None,
                port     = port or (_port and int(_port)) or None,
                username = username or _username or None,
                password = password or _password or None,
                secure   = secure if secure is not None else _scheme == 'https',
            )

        # Override path if explicitly passed
        if path is not None:
            self.path = path

        # Override fragment if explicitly passed
        if fragment is not None:
            self.fragment = fragment

        # Create the query dictionary and add kwargs to it
        self.query = {}
        if _query_string is not None:
            self.query.update(dict(urllib.parse.parse_qsl(_query_string)))
        if query_string is not None:
            self.query.update(dict(urllib.parse.parse_qsl(query_string)))
        if query is not None:
            self.query.update(query)
        self.query.update(kwargs)

    @property
    def query_string(self):
        return Query(self.query, self.verbatim)

    @property
    def userinfo(self):
        return (self.connection.username,
                self.connection.password)

    @property
    def host_parts(self):
        return (self.connection.scheme,
                self.connection.netloc)

    @property
    def absolute_path_parts(self):
        return (self.path,
                self.query_string,
                self.fragment)

    @property
    def parts(self):
        return self.host_parts + self.absolute_path_parts

    @property
    def authority(self):
        return urllib.parse.urlunsplit(self.host_parts, + ('', '', ''))


    @property
    def absolute_path(self):
        """
        Return the url string without scheme and netloc parts
        """
        return urllib.parse.urlunsplit(('', '') + self.absolute_path_parts)

    @property
    def url(self):
        return urllib.parse.urlunsplit(self.parts)

    def stream(self, method='GET', body=None, headers=None, **kwargs):
        return Request(resource=self, method=method, body=body).stream(**kwargs)

    def __call__(self, **kwargs):
        return Request(resource=self, **kwargs)

    def __str__(self):
        """
        Return a string containing the complete url.
        """
        return self.url


class URL(str):
    def __new__(self, *args, **kwargs):
        return str.__new__(self, Resource(*args, **kwargs).url)


class AbsolutePath(str):
    def __new__(self, *args, **kwargs):
        return str.__new__(self, Resource(*args, **kwargs).absolute_path)


def add_user_agent(method, url, body, headers):
    headers['User-Agent'] = headers.pop('User-Agent', USER_AGENT)
    return method, url, body, headers

class Request:
    """
    A full HTTP request that is fired when called.
    """
    class Error(Error): pass

    def __init__(
            self,
            url = '',
            method = 'GET',
            body = None,
            mode = 'call',
            headers = None,
            resource = None,
            data = None,
            processors = None,
            **kwargs
    ):
        self.resource = resource or Resource(url, **kwargs)

        self.mode = mode
        self.method = method
        self.headers = headers or {}
        self.body = body
        self.data = data or {}


        # A processor is a callable that takes 4 arguments
        # (method, url, body, headers)
        # And returns a same tuple with possibly modified values
        self.processors = [add_user_agent]
        if processors:
            if isinstance(processors, collections.Iterable):
                self.processors.append(processors)
            else:
                self.processors.extend(processors)

    @property
    def params(self):
        method = self.method.upper()

        url = self.resource.absolute_path

        if self.body is None and self.data and method in ('POST', 'PUT', 'PATCH'):
            body = Query(**self.data)
        else:
            body = self.body

        headers = self.headers.copy()

        args = (method, url, body, headers)

        for processor in self.processors:
            args = processor(*args)
        return args

    def stream(self, **kwargs):
        return self.resource.connection.start(self, **kwargs)

    def __call__(self):
        return self.resource.connection.fetch(*self.params)

    def __str__(self):
        return '{} {}'.format(self.method.upper(), self.resource)


class Connection:
    """
    Requires the inheritor to have a domain string field.
    """
    host = None
    auth = None
    secure = False
    method = 'GET'
    mode = 'call'
    format = None
    streaming = False

    port = None
    strict = False
    timeout = 5.0  # seconds
    reconnect_time = 5.0  #seconds
    exceptions = False

    auto_connect = True
    auto_request = False

    headers = {}

    processors = ()

    connection = None

    username = None
    password = None

    def __init__(self, host=None, **kwargs):
        if host:
            self.host = host
        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def netloc(self):
        if (self.port is not None
        and not (self.port == http.client.HTTP_PORT and self.scheme == 'http')
        and not (self.port == http.client.HTTPS_PORT and self.scheme == 'https')):
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
        if self.secure:
            return 'https'
        else:
            return 'http'

    def connect(self, host=None, port=None, timeout=None, strict=None):
        """
        Open the appropriate connection with the specified host.
        """
        # Return if the connection is opened already
        if self.connection is not None:
            return

        # Specify the connection type
        if self.secure:
            connector = http.client.HTTPSConnection
        else:
            connector = http.client.HTTPConnection

        # Prepare parameters
        params = {}
        for attr in ('host', 'port', 'strict', 'timeout'):
            val = locals().get(attr)
            params[attr] = getattr(self, attr) if val is None else val

        # Open the connection
        self.connection = connector(**params)

    def reconnect(self, reconnect_time=None):
        """
        Disconnect and then connect after sleeping passed or default seconds.
        """
        self.disconnect()
        if reconnect_time is None:
            reconnect_time = self.reconnect_time
        time.sleep(reconnect_time)
        self.connect()

    def disconnect(self):
        """
        Close the connection if it is open.
        """
        if self.connection is None:
            return
        self.connection.close()
        self.connection = None

    def request(self, method, url, body=None, headers={}):
        """
        Issue a request on the connection. Open a connection if needed and
        apply all processors to the request parameters.
        """
        # Open a connection if it is not manually handled
        if self.auto_connect:
            self.connect()
        _headers = self.headers.copy()
        _headers.update(headers)

        params = method, url, body, _headers

        for processor in self.processors:
            params = processor(params)

        self.connection.request(*params)

    def getresponse(self, **kwargs):
        """
        Return a Response object, potentially in a predifined format.
        """
        _response = self.connection.getresponse()
        response = Response(_response, streaming=self.streaming, exceptions=self.exceptions)

        # Close the connection if it is not manually handled
        if self.auto_connect:
            self.disconnect()

        # Return parsed if specified
        format = kwargs.pop('format', self.format)
        if format:
            return getattr(response, format)
        return response

    #XXX: needs work on arguments
    def fetch(self, *args, **kwargs):
        self.request(*args, **kwargs)
        return self.getresponse()

    def build_request(self, *args, **kwargs):
        """
        Return a Request constructor
        """
        method = kwargs.pop('method', self.__class__.method)
        secure = kwargs.pop('secure', self.__class__.secure)
        mode = kwargs.pop('mode', self.__class__.mode)

        self.format = kwargs.pop('format', self.__class__.format)

        return Request(*args, connection=self, processors=self.processors,
                method=method, secure=secure, mode=mode)

    def open(self, *args, **kwargs):
        return self.build_request(*args, **kwargs)()

    def get(self, *args, **kwargs):
        kwargs['method'] = 'GET'
        return self.open(*args, **kwargs)

# Add get, post, ... api to Connection class
'''
for method in METHODS:
    setattr(Connection, method.lower(), lambda self, *args, **kwargs:
            self.open(*args, method=method, **kwargs))

'''


class Response:
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
    class Error(Error): pass
    class ParseError(Error): pass

    def __init__(self, response, streaming=False, exceptions=False):
        self.response = response
        self.headers = dict(response.getheaders())

        status = self.response.status
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
            return self.__dict__[attr]
        except KeyError:
            return getattr(self.response, attr)

    def readline(self, delimiter='\r\n'):
        """Return data read up to first occurrance of delimiter."""
        data = ''
        while not data.endswith(delimiter):
            data += self.read(1)
        # Exclude delimiter from return data
        return data[:-len(delimiter)]

    @property
    def old_raw(self):
        if not hasattr(self, '_raw'):
            self._raw = self.response.read()
        return self._raw

    @property
    def utf8(self):
        return self.raw.decode('utf8')

    @property
    def html(self):
        return self.utf8

    @property
    def json(self):
        try:
            return json.loads(self.utf8)
        except Exception as e:
            raise self.ParseError("Could not parse json from data!", e)

    @property
    def xml(self):
        try:
            return xml.dom.minidom.parseString(self.utf8)
        except Exception as e:
            raise self.ParseError("Could not parse xml from data!", e)

    @property
    def query(self):
        return dict(urllib.urlparse.parse_qsl(self.raw))

    @property
    def content(self):
        """Do something smart to the data to discover its type"""
        return self.raw


class Listener:
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        return False

    def on_timeout(self):
        """Called when stream connection times out"""
        return True

class WriteListener(Listener):
    def __init__(self, filename):
        self.filename = filename

    def on_data(self, data):
        with open(self.filename, 'a') as handle:
            handle.write(data)


class Stream(Connection):
    auto_connect = False
    timeout = 300.0
    retry_count = None
    snooze_time = 5.0
    buffer_size = 1500
    secure = True
    mode = 'stream'
    streaming = True

    running = False
    endpoint = None
    _response = None

    class Error(Error): pass

    def __init__(self, host=None, auth=None, listener=None, **options):
        if host:
            self.host = host
        self.listener = listener or Listener()
        self.auth = auth

        OPTIONS = ("timeout", "retry_count", "retry_time",
                   "snooze_time", "buffer_size", "secure",)

        for key in OPTIONS:
            setattr(self, key, options.get(key, getattr(self, key)))

    def retry_time(self, error_count):
        return 10.0

    def read(self, amount):
        if not self.running or self.response.isclosed():
            return None
        return self.response.read(amount)

    def readline(self, delimiter='\r\n'):
        if not self.running or self.response.isclosed():
            return None
        return self.response.readline(delimiter)

    def _run(self):
        # Connect and process the stream
        error_counter = 0
        exception = None

        self.connect()
        print('connected, running:', self.endpoint)
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                break
            try:
                print('ITER')
                resp = self.endpoint()
                print(resp.status)
                if resp.status != 200:
                    if self.listener.on_error(resp.status, error_counter) is False:
                        break
                    error_counter += 1
                    time.sleep(self.retry_time(error_counter))
                else:
                    error_counter = 0
                    self._read_loop(resp)
            except socket.timeout:
                print('TIMEOUT')
                if self.listener.on_timeout() == False:
                    break
                if not self.running:
                    break
                self.reconnect(self.snooze_time)
            except Exception as exception:
                print('EXCEPTION', exception)
                # any other exception is fatal, so kill loop
                break

        # cleanup
        self.running = False
        self.disconnect()

        if exception:
            raise

    def _read_loop(self, response):
        self.response = response
        while self.running and not response.isclosed():
            data = self.read_loop_iter()
            if self.listener.on_data(data) is False:
                self.running = False
        self.response = None

        if response.isclosed():
            self.on_closed(response)

    @property
    def stream(self):
        self._cache('mode', 'stream')
        return self

    def start(self, callm=None, async=False):
        """Open a stream with a callm request."""
        if callm:
            self.endpoint = callm
        if self.running is True:
            raise self.Error('Stream running already!')
        self.running = True
        print('RUNNING')
        if async:
            threading.Thread(target=functools.partial(self._run)).start()
        else:
            self._run()

    def stop(self):
        """Close the running stream on this Creek."""
        self.running = False

    def on_closed(self, response):
        """Called when the response has been closed by the host."""
        pass

    def read_loop_iter(self):
        """
        Return one packet of data read from the response. Should normally be
        overwritten by subclass.
        """
        c = ''
        data = ''
        while c != '\n':
            c = self.read(1)
            data += c
        return data


# namespace api
open = lambda url, **kwargs: Request(url=url, **kwargs)()

for method in METHODS:
    globals()[method.lower()] = functools.partial(open, method=method)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
