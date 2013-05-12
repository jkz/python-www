import sys

import www

class Error(www.Error):
    pass

class Auth:
    """
    Authorizes requests with given credentials
    """
    def __init__(self, consumer, token=None, **options):
        self.consumer = consumer
        self.token = token
        self.options = options

    def __call__(self, url, method, headers, body):
        """
        Return signed request parameters.
        """
        return url, method, headers, body


class Service:
    def __init__(self, provider):
        self.provider = provider


def _get_nearest_class(cls, name):
    try:
        return getattr(cls, name)
    except AttributeError:
        pass

    try:
        return getattr(sys.modules[cls.__module__], name)
    except AttributeError:
        pass

    for base in cls.__bases__:
        ret = _get_nearest_class(base, name)
        if ret:
            return ret
    return None

class InterfaceClassAttribute:
    """
    This funny construct allows interface parts to be defined in
    a module and recognized by the class. It will find the 'nearest'
    class with the given name in the modules of the bases of the
    original object's class.

    You can also assign a class to override this behaviour.
    """
    def __init__(self, name):
        self.name = name
        self.classes = {}

    def __get__(self, obj, objtype):
        for base in ((objtype,) + objtype.__bases__):
            if not base in self.classes:
                try:
                    cls = getattr(sys.modules[base.__module__], self.name)
                except AttributeError:
                    continue
                self.classes[base] = cls
                return cls
            else:
                return self.classes[base]
        raise NotImplemented

    def __set__(self, obj, val):
        self.classes[obj.__class__] = val


class Consumer:
    """
    Represents an authenticating entity.
    """
    # A class that authorizes requests by signing their parameters
    Auth = InterfaceClassAttribute('Auth')

    # A class that provides the authentication service
    Provider = InterfaceClassAttribute('Provider')

    # A class that executes authenticated calls
    API = InterfaceClassAttribute('API')

    def get_user(self, **creds):
        """Return a user object for given credentials (or None)"""
        return NotImplementedError

    def get_token(self, user):
        """Return a token object for given user"""
        return NotImplementedError


    @property
    def auth(self):
        return self.Auth(consumer=self)

    @property
    def provider(self):
        return self.Provider(auth=self.auth)

    @property
    def api(self):
        return self.API(auth=self.auth)


class Token:
    """
    Represents a user authorization for a consumer
    """
    consumer = Consumer()

    @property
    def auth(self):
        return self.consumer.Auth(self.consumer, self)

    @property
    def api(self):
        return self.consumer.API(auth=self.auth)


