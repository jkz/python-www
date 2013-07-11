import copy

from . import exceptions

class Option:
    """
    The Option class extracts options from an object.
    """
    # A dictionary of container accessors with signature
    #    accessor(self, obj, param)
    containers = {}

    # The order in which the containers should be accessed
    order = ()

    # A dictionary mapping containers keys to either:
    #     param
    # OR
    #     tuple(param, converter)
    options = {}

    # The field that validates and converts the actual value
    field = None

    def __init__(self, **conf):
        #XXX methods and requires are not used at the moment
        """
            as_query    # query parameter option key
            as_kwarg    # url kwargs option key
            as_header   # headers option key
            as_meta     # cgi env option key
            as_lambda   # function takes a request and returns a value
            as_method   # a method name on the option's host class

            methods     # http methods supporting the option
            requires    # function takes a request and returns permission flag

            field       # a field object, most config goes in there
        """
        self.lookup = conf.pop('options', {})
        for key, val in conf.items():
            if key.startswith('as_'):
                self.options[key] = val
            else:
                setattr(self, key, val)

    def lookup_ordered(self):
        for container in self.order:
            if container in self.options:
                yield container

    def extract(self, object, param, convert=None):
        try:
            value = self.containers[container](self, object, param)
        except (KeyError, AttributeError):
            raise Missing

        if convert:
            return convert(value)
        return value

    def find(self, object):
        for pair in self.lookup_ordered():
            if isinstance(pair, (list, tuple)):
                param, convert = pair
            else:
                param, convert = pair, None

            try:
                return self.extract(object, param, convert)
            except exceptions.Missing:
                continue
        else:
            raise exceptions.Missing

    def meta(self):
        meta = {}
        meta['options'] = self.options
        meta['field'] = self.field.meta()
        return meta

    def parse(self, object):
        try:
            value = self.find(object)
        except exceptions.Missing:
            value = self.field.nulls[0]
        return self.field.parse(value)


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
        Return an iterator yielding all name, value pairs for configured
        options.
        """
        for name, option in self.options:
            try:
                yield name, option(object)
            except exceptions.Missing:
                raise
            except exceptions.Omitted:
                continue

    def meta(self):
        """
        For each callable, either use its meta method results or docstring
        as meta info.
        """
        meta = {}
        for name, option in self.items():
            try:
                meta[name] = option.meta()
            except attributeError:
                meta[name] = option.__doc__
        return meta

