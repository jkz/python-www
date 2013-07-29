
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

