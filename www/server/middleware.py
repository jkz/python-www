import www

def to_tuple(thing):
    """
    Takes a dictionary, function or collection and turns it into a tuple
    """
    try:
        thing = thing.items()
    except AttributeError:
        try:
            thing = thing()
        except TypeError:
            thing = tuple(thing)

    if isinstance(thing, tuple):
        return thing

    return to_tuple(thing)


class Middleware:
    """
    Middelwares are layers of the www server stack. A request passes through a set
    of layers, each one optionally enriching the request object, guarding
    passage, look for cache entries and returning a response.

    This middleware is not compatible with wsgi, but models the principle with
    a reqeust object as environ and envelope as start_response.
    """
    options = ()
    guards = ()
    caches = ()

    def __init__(self, app):
        self.app = app

    def envelope(self, status, meta):
        return status, meta

    #TODO, think of envelope
    def apply(self, request, envelope=None):
        """
        Return anything that a calling layer would like to see.
        To shortcut a response, raise an exception or Reponse.
        """
        return self.resolve(request)

    def _flatten(self, attr):
        for level in (
                getattr(self, 'default_' + attr),
                getattr(self, attr),
                getattr(self, 'extra_' + attr)):
            for el in to_tuple(level):
                yield el

    def option(self, request):
        """Update the request object with parsed options"""
        for o in self._flatten('options'):
            if callable(o):
                o(request)
                continue

            name, pairs = o

            if callable(pairs):
                request[name] = pairs(request, self)
                continue

            try:
                default = (getattr(self, name),)
            except AttributeError:
                default = ()

            request[name] = request.setdefault(name, *(tuple(pairs) + default))

    def guard(self, request):
        """Run all conditional rejection checks"""
        for g in self._flatten('guards'):
            g(request)

    def cache(self, request):
        """Look for available data in caches and raise any yielded responses"""
        for c in self._flatten('caches'):
            c(request)

    def __call__(self, request, *args, **kwargs):
        #TODO if request:
        if False:
            self.option(request)
            self.guard(request)
            self.cache(request)
        return self.apply(request, *args, **kwargs)


#XXX This is dark magic. Might not be in line with the filosophy
#TODO set options? append options? udpate options?
def options(*args, **kwargs):
    options = layers.to_tuple(kwargs) + args
    def decorator(func):
        # Set the options of a layer
        if isinstance(func, layers.Layer):
            func.options = options
            return func

        # Turn the function into a layer and set the options
        class Layer(layers.Layer):
            options = layers.to_tuple(kwargs) + args

            def call(self, *args, **kwargs):
                return func(*args, **kwargs)
        #XXX Some extra work to make the class look more like the function
        #    would be nice.
        return Layer()

def guards(*args, **kwargs):
    #TODO same as above
    pass

def caches(*args, **kwargs):
    #TODO same as above
    pass

def layer(options=(), guards=(), caches=()):
    def decorator(func):
        if isinstance(func, layers.Layer):
            pass


class Middleware:
    def __init__(self, application):
        self.application = application

    def envelope(self, code, headers):
        pass

    def resolve(self, request, envelope):
        pass

    def __call__(self, request, envelope):
        self.resolve(request, envelope)
        self.application(request, self.envelope)
