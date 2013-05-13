import sys

import www

class InterfaceClassAttribute:
    """
    This funny construct allows interface parts to be defined in
    a module and recognized by the class. It will automagically
    find the 'nearest' class with the given name in the modules
    of the bases of the original object's class.

    You can also assign a class to override this behaviour.
    """
    #XXX I wrote this stoned and it worked at the first try
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
        raise NotImplementedError

    def __set__(self, obj, val):
        self.classes[obj.__class__] = val


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

    def __call__(self, request):
        pass

class Service:
    # A class that authorizes requests by signing their parameters
    Auth = InterfaceClassAttribute('Auth')

    # A class that configures the connection used by this service
    Connection = InterfaceClassAttribute('Connection')

    """
    A class which makes authenticated requests to a configured connection.
    """
    def __init__(self, **kwargs):
        try:
            self.connection = kwargs['connection']
        except KeyError:
            self.conneciton = self.Connection()
        self.auth = self.Auth(**kwargs)

        self.connection.processors.append(self.auth)


class Consumer:
    """
    Represents an authenticating entity.
    """
    # A Service class that provides authorization credentials
    Authority = InterfaceClassAttribute('Authority')

    # A class that executes authenticated calls
    API = InterfaceClassAttribute('API')

    def get_user(self, **creds):
        """Return a user object for given credentials (or None)"""
        return NotImplementedError

    def get_token(self, uid):
        """Return a token object for given user id (or None)"""
        return NotImplementedError


    @property
    def authority(self):
        return self.Authority(consumer=self)

    def api(self, **kwargs):
        return self.API(consumer=self, **kwargs)


class Token:
    """
    Represents a user authorization for a consumer
    """
    Consumer = InterfaceClassAttribute('Consumer')

    @property
    def consumer(self):
        return self.Consumer()

    def api(self):
        return self.consumer.API(token=self)

