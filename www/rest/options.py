import copy

from . import exceptions
from .validators import Validators

def get_ip(request):
    """Extract the caller's IP"""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.meta.get('REMOTE_ADDR')
    return ip

class Option:
    """
    The Option class extracts options from a request object.
    """
    empty = (None, (), [], {})
    validators = Validators()

    def __init__(self, **conf):
        """
            as_query    # query parameter option key
            as_kwarg    # url kwargs option key
            as_header   # headers option key
            as_meta     # cgi env option key
            as_lambda   # function takes a request and returns a value
            as_method   # a method name on the option's host class
            default
            choices     # the valid values for this option
            help_text   # description for client side
            convert     # function that takes a value and returns one
            methods     # http methods supporting the option
            requires    # function takes a request and returns permission flag
            validators  # functions that takes the value and raises exceptions
        """
        validators = conf.pop('validators')
        if validators:
            self.validators += validators
        self.__dict__.update(conf)

    containers = {
        'as_query':  lambda r: r.query,
        'as_kwarg':  lambda r: r.kwargs,
        'as_header': lambda r: r.headers,
        'as_meta':   lambda r: r.meta,
    }

    def find(self, request):
        if 'as_query' in self.conf:
            try:
                return request.query[self.conf['as_query']]
            except KeyError:
                pass

        if 'as_kwarg' in self.conf:
            try:
                return request.kwargs[self.conf['as_kwarg']]
            except KeyError:
                pass

        if 'as_header' in self.conf:
            try:
                return request.headers[self.conf['as_header']]
            except KeyError:
                pass

        if 'as_meta' in self.conf:
            try:
                return request.meta[self.conf['as_meta']]
            except KeyError:
                pass

        if 'as_lambda' in self.conf:
            return self.as_lambda(request)

        if 'as_method' in self.conf:
            return getattr(self, self.conf['as_method'])(request)

        if 'default' in self.conf:
            return self.conf['default']

        raise exceptions.Missing


    def meta(self):
        return self.conf

    def __call__(self, request, caller=None):
        if 'as_method' in self.conf:
            return getattr(caller, self.conf['as_method'])(request)

        if 'requires' in self.conf and not self.conf['requires'](request):
            return

        val = self.find(request)

        if 'convert' in self.conf:
            return self.conf['convert'](val)

        return val


class Integer(Option):
    min = None
    max = None

    empty = (None, 'none')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators += (
            validators.Min(self.min),
            validators.Max(self.max),
        )

    def convert(self, value):
        if value in self.empty:
            return None
        return int(value)

class Options(dict):
    """A dictionary of callables that extract arguments from objects"""

    def __add__(self, other):
        """
        Create a deepcopy of self and update it with a deepcopy of the other.
        """
        #XXX maybe a more procedural approach is preferred here
        if not isinstance(other, Options):
            raise TypeError
        new = copy.deepcopy(self)
        new.update(copy.deepcopy(other))
        return new

    def __radd__(self, other):
        return self + other

    def parse(self, object):
        """
        Return an iterator containing all name, value pairs for configured
        options.
        """
        for name, option in self.options:
            try:
                yield name = option(object)
            except exceptions.Missing:
                raise
            except exceptions.Omitted:
                continue

    def meta(self):
        meta = {}
        for name, option in self.items():
            try:
                meta[name] = option.meta()
            except attributeError:
                meta[name] = option.__doc__
        return meta

