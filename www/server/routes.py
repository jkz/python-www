#XXX Feature requests:
# - Route.append(route)
# - Part shortcuts like /:slug/#uid or /<str:slug>/<int:uid>
# - Part shortcut tuples:
#       int
#       str
#       (int, '[0-9]+')
#       (str, '[^/]+')
"""
This module enables you to configure a routing scheme, to map urls to
endpoints and extract keyword arguments from those urls.

The mapping scheme is a bijection:
    resolve maps url to endpoint + kwargs
    reverse maps names + kwargs to urls
"""
import collections
import re

from www import shortcuts
from www.server import responses
from www.utils.decorators import lazy_property

#XXX Needs test coverage
#XXX Needs fields
class Part:
    """
    An argument in a route pattern, eg.
        uid = Kwarg('uid')

        /resource/{uid}

    """
    pattern = '[^/]+'
    def __init__(self, pattern=None, convert=None):
        if pattern is not None:
            self.pattern = pattern
        if convert:
            self.convert = convert

    def convert(self, val):
        return val

    def resolve(self, val):
        return self.convert(val)

    def reverse(self, val):
        return str(val)

    def __str__(self):
        return self.pattern

class Parts(Part):
    def __init__(self, pattern=None, convert=None, separator=None):
        super().__init__(pattern, convert)
        if separator:
            self.separator

    def resolve(self, val):
        return tuple(int(v) for v in val.split(self.separator))

    def reverse(self, val):
        return self.separator.join(str(v) for v in val)

    def __str__(self):
        return '{pat}(?:{sep}{pat})+'.format(pat=self.pattern, sep=self.separator)


class Str(Part):
    pattern = '[^/]+'

class Int(Part):
    pattern = '[0-9]+'

    def convert(self, val):
        return int(val)

class Strs(Parts):
    separator = ','

class Ints(Parts):
    separator = ';'

    def convert(self, val):
        return int(val)


class Route:
    # Serial number to retain pattern order in kwarg declaration,
    # which would otherwise be undefined.
    #XXX Behaviour when a predeclared route is assigned to a
    #    router later, it might be unintendedly first
    _last_serial = 0

    def __init__(self, pattern, endpoint=None, **kwargs):
        self._serial = Route._last_serial = self._last_serial + 1
        self.pattern = pattern
        self.endpoint = endpoint
        self.routes = collections.OrderedDict()
        self._parts = {}

        routes = []

        for key, val in kwargs.items():
            # Add nested routes
            if isinstance(val, Route):
                routes.append((key, val))
            # Add url parts
            else:
                self._parts[key] = val

        # Add the routes sorted by serial
        for key, val in sorted(routes, key=lambda x: x[1]._serial):
            self.routes[key] = val

        self._compiled = re.compile(str(self))

    def __getattr__(self, attr):
        # Expose nested routes as attributes by their name
        try:
            return self.routes[attr]
        except KeyError:
            raise AttributeError

    @lazy_property
    def endpoints(self):
        """
        Build a map of endpoints to full endpoint names, so they can be
        reversed.
        """
        endpoints = {self.endpoint, self.name}
        for route in self.routes:
            for endpoint, name in route.endpoints.items():
                endpoints[endpoint] = '{}.{}'.format(self.name, name)
        return endpoints


    def reverse(self, name='', **kwargs):
        """
        Usage:

        route.reverse('foo.bar', **kwargs)

        Build an url by recursively replacing kwargs and appending
        reversed nested routes.

        OR

        route.reverse(Endpoint, **kwargs)
        """
        if not isinstance(name, str):
            name = self.endpoints[name]

        # Prepare the arguments for the path
        format_args = {key: part.reverse(kwargs.pop(key))
                for key, part in self._parts.items()}
        # Format the path pattern
        path = self.pattern.format(**format_args)

        # Append nested route paths
        if name:
            name, dot, rest = name.partition('.')
            path += getattr(self, name).reverse(rest, **kwargs)
        elif kwargs:
            path = shortcuts.absolute(path, query=kwargs)

        # Return the total path from this part to the end
        return path


    def resolve(self, path='', **kwargs):
        """
        Check if the path matches the pattern, if not, return None.
        If so, check if the remainder matches a nested pattern.
        If so, return its endpoint, else your own. Also combine all kwargs
        found on the way.
        """
        match = self._compiled.match(path)
        if not match:
            return

        kwargs = match.groupdict()
        for key, val in kwargs.items():
            # These groups are for match parts
            if key in self._parts:
                kwargs[key] = self._parts[key].resolve(val)
            # These are directly from the pattern
            else:
                kwargs[key] = val

        # Subtract the matched part from the path
        unmatched = path[match.end():]

        # Look for a deeper match and return it if found
        for route in self.routes.values():
            deeper = route.resolve(unmatched)
            if deeper:
                endpoint, _kwargs = deeper
                kwargs.update(_kwargs)
                return endpoint, kwargs

        # Did not match the entire string and did not match a nested route
        if unmatched:
            return None

        # Return the endpoint and the matched, processed kwargs
        return self.endpoint, kwargs

    def __str__(self):
        """
        Format the named pattern groups and return the full pattern.
        """
        return self.pattern.format(**{ k: '(?P<{}>{})'.format(k, v)
                for k, v in self._parts.items()})

