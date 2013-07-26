import copy

from . import exceptions

class Lookup:
    container = None
    param = None

    def __init__(self, container, param, convert=None):
        self.container = container
        self.param = param
        if convert:
            self.convert = convert

    def convert(self, option, value):
        return value

    def __call__(self, value):
        pass


class Option:
    """
    The Option class extracts options from an object. The Option object has a
    set of containers and on order in which these containers are to be
    consulted. The containers are specified by functions with a signature of
    container(
        self, # the option
        obj,  # the object to extract from
        param # the configured parameter for this option
    )
    """
    # A dictionary of container accessors with signature
    #    accessor(self, obj, param)
    containers = {}

    # The order in which the containers should be accessed. Each value
    # in order is checked for presence as attribute and returned as either
    order = ()

    # A dictionary mapping containers keys to either:
    #     param
    # OR
    #     tuple(param, converter)
    # This ditionary exists so it can easily be overwritten entirely
    options = {}

    # The field that validates and converts the actual value
    field = None

    def __init__(self, **conf):
        # First take out the options parameter, or create a new
        self.options = conf.pop('options', copy(self.options))
        self.order = conf.pop('order', self.order)

        # Add all attributes present in order to options
        for key, val in self.__dict__.items():
            if key in self.order:
                self.options[key] = val

        for key, val in conf.items():
            # Add all arguments present in order to options
            if key in self.order:
                self.options[key] = val
            # Add all other arguments as attributes
            else:
            setattr(self, key, val)

    def lookups_ordered(self):
        for container in self.order:
            if hasattr(self, container):
                yield container, getattr(self, container)

    def parse(self, container, value):
        parser = self.parsers.get(container)
        if not parser:
            parser = getattr(self, 'parse_' + container)
        else:
            return value
        return parser(value)

    def extract(self, container, object, param):
        try:
            value = self.containers[container](self, object, param)
        except (KeyError, AttributeError):
            raise exceptions.Missing
        return self.parse(container, value)

    def find(self, object):
        for container, pair in self.lookups_ordered():
            if isinstance(pair, (list, tuple)):
                param, convert = pair
            else:
                param, convert = pair, None

            try:
                return self.extract(container, object, param, convert)
            except exceptions.Missing:
                continue
        else:
            if self.field.default:
                return self.field.default
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
        for name, option in self.items():
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

