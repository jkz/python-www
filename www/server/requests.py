import collections

from .headers import Header
from . import exceptions

class Request(Request, collections.UserDict):
    """
    This class is the request description, it contains all
    arguments and options, and is passed through all layers of the
    application.
    """

    #TODO would be nice to show the actual key
    error = KeyError("Key not found in options.")

    def __init__(self, path, method='GET', body=None, headers=None,
            query=None, meta=None, args=None, kwargs=None, options=None):

        # Changable by options
        self.method = method

        # Read-only values
        self.path = path

        try:
            self.body = body.decode('utf-8')
        except AttributeError:
            self.body = body

        # Read-only containers
        self.args = args or ()
        self.kwargs = args or {}
        self.query = query or {}
        self.meta = meta or {}
        self.headers = headers or {}

        # Options store (preferably used through request object as dict]
        self.options = options or {}

    def location(self, resource, *args, **kwargs):
        return self.path

    def default(self, default=error):
        # If default is an exception, raise it, else return its value.
        # Small caveat is that this cannot raise TypeErrors.
        # Ambiguous shoutout to Beautiful is better than ugly.
        try:
            raise default
        except TypeError:
            return default

    def find(self, name, key, *parsers):
        # Non-string iterables are split into a name, key, *parsers pair
        # The key is looked up in given container name and optionally parsed
        try:
            container = getattr(self, name)
        except AttributeError:
            raise exceptions.ConfigurationError(
                "{} container specified in option does not exist".format(name))
        val = container[key]

        for parser in parsers:
            val = parser(val)
        return val

    def parse(self, *options):
        for o in options:
            # Callable options are called with the request as argument
            if callable(o):
                return o(self)

            if not isinstance(o, str):
                try:
                    return self.find(*o)
                # Try next option if not found
                except KeyError as e:
                    continue
                # Return or raise value if it is not an option
                except TypeError as e:
                    return self.default(o)
            return self.default(o)
        return None

    def get(self, key, *options):
        try:
            return self[key]
        except KeyError:
            return self.parse(*options)

    def set(self, key, *options):
        self[key] = self.parse(*options)

    def setdefault(self, key, *options):
        """Simultaneously get and set a value"""
        val = self[key] = self.get(key, *options)
        return val

    def update(self, pairs):
        # Convert dictionary to a list of pairs
        # Boobs! The order is undefined, so using callables in dict options is
        # discouraged.

        if hasattr(pairs, 'items'):
            for key, options in pairs.items():
                self.set(key, *options)
        else:
            # Takes a list of key, options pairs and set them
            for key, options in pairs:
                self.set(key, *options)

    # Make request behave like a dict
    def __iter__(self):
        return self.options.__iter__()

    def __getitem__(self, key):
        o = self.options
        return self.options[key]

    def __setitem__(self, key, val):
        self.options[key] = val

    def __delitem__(self, key):
        del self.options[key]

    def __len__(self):
        return len(self.options)

    def debug(self):
        print(10*'=', 'DEBUG REQUEST', 10*'=')
        print(self.method, self.path)
        print('query')
        for x in self.query.items():
            print ('  ', *x)
        print('options')
        for x in self.query.items():
            print ('  ', *x)
