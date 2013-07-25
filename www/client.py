import www.http

class Request(www.http.Request):
    def params(self):
        self.prepare()

        method = self.method.upper()

        url = self.resource.path

        if self.body is None and self.data and method in ('POST', 'PUT', 'PATCH'):
            body = www.http.Query(**self.data)
        else:
            body = self.body

        headers = self.headers.copy()
        return (method, url, body, headers)

    def stream(self, **kwargs):
        return self.resource.connection.start(self, **kwargs)

    def __call__(self):
        return self.resource.connection.fetch(*self.params())


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

    processors = []  #XXX care, this is a mutable class property

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
            connector = http.HTTPSConnection
        else:
            connector = http.HTTPConnection

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
        Issue a request on the connection. Open a connection if needed.
        """
        # Open a connection if it is not manually handled
        if self.auto_connect:
            self.connect()
        _headers = self.headers.copy()
        _headers.update(headers)

        params = method, url, body, _headers

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

    def create_request(self, *args, **kwargs):
        """
        Return a request object.
        """
        method = kwargs.pop('method', self.__class__.method)
        secure = kwargs.pop('secure', self.__class__.secure)
        mode = kwargs.pop('mode', self.__class__.mode)

        self.format = kwargs.pop('format', self.__class__.format)

        return Request(*args, connection=self, processors=self.processors,
                method=method, secure=secure, mode=mode)

    def open(self, *args, **kwargs):
        return self.create_request(*args, **kwargs)()

    #TODO: add this api more nicely
    #TODO: choose upper or lower
    def GET(self, *args, **kwargs):
        kwargs['method'] = 'GET'
        return self.open(*args, **kwargs)

    def POST(self, *args, **kwargs):
        kwargs['method'] = 'POST'
        return self.open(*args, **kwargs)

# Add get, post, ... api to Connection class
'''
for method in METHODS:
    setattr(Connection, method.lower(), lambda self, *args, **kwargs:
            self.open(*args, method=method, **kwargs))

'''


class Response:
    """
    Response from a request.
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
        return dict(parse_qsl(self.raw))

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

    def __init__(self, host=None, listener=None, **options):
        if host:
            self.host = host
        self.listener = listener or Listener()

        OPTIONS = ("timeout", "retry_count", "retry_time",
                   "snooze_time", "buffer_size", "secure",)

        for key in OPTIONS:
            setattr(self, key, options.pop(key, getattr(self, key)))

        for key, val in options.items():
            setattr(self, key, val)

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

    def start(self, endpoint=None, async=False):
        """Open a stream with a request object"""
        if endpoint:
            self.endpoint = endpoint
        if self.running is True:
            raise self.Error('Stream running already!')
        self.running = True
        print('RUNNING')
        if async:
            threading.Thread(target=functools.partial(self._run)).start()
        else:
            self._run()

    def stop(self):
        """Close the running stream"""
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
