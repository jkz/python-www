import www
import re

#XXX Needs test coverage
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
    """
    Use like this.

    Doesnt look all too sexy in comments :/

    api = Route('/api', Api.Index,
        users = Route('/users', User.All,
            one = Route('/{uid}', User.One, uid=Int(),
                posts = Route('/posts', UserPosts.All),
            few = Route('/{uids}', User.Few, uids=Ints()),
        posts = Route('/posts', Post.All),
            one = Route('/{uid}', Post.One, uid=Int()),
            few = Route('/{uids}', User.Few, uids=Ints()),

    Also allows:
    api = Route('/api', Api.Index,
        users       = Route('/users', User.All)
        user        = Route('/users/(?P<uid>[^/]+)', User.One)
        user_posts  = Route('/users/(?P<uid>[^/]+)/posts', UserPosts.All),
    )
    """
    _last_serial = 0

    def __init__(self, pattern, endpoint=None, **kwargs):
        self._serial = self._last_serial = self._last_serial + 1
        self.pattern = pattern
        self.endpoint = endpoint

        # There are 4 special cases in `parts` that map to classes
        # - str
        # - int
        # - [str]
        # - [int]
        # There are some more to be implemented
        # - 'pattern',
        # - convertor,
        # - ['pattern'],
        # - [convertor],
        # - ['pattern', convertor]
        # - ['pattern', convertor, 'sep']
        # - ['pattern', 'sep']
        # - [convertor, 'sep']
        '''
        for key, val in parts.items():
            if val == str:
                self._parts[key] = Str()
            elif val == int:
                self._parts[key] = Int()
            elif val == [str]:
                self._parts[key] = Strs()
            elif val == [int]:
                self._parts[key] = Ints()
            else:
                self._parts[key] = val
        '''
        self._routes = []
        self._parts = {}
        for key, val in kwargs.items():
            if isinstance(val, Route):
                self._routes.append(val)
                setattr(self, key, val)
            else:
                self._parts[key] = val
        self._routes = sorted(self._routes, key=lambda x: x._serial)
        self._compiled = re.compile(str(self))

    def reverse(self, name='', **kwargs):
        """
        Usage:

        route.reverse('foo.bar', **kwargs)

        Builds an url by recursively replacing kwargs and accessing appending
        resolved nested route.
        """
        # Prepare the arguments for the path
        fargs = {key: part.reverse(kwargs.pop(key))
                for key, part in self._parts.items()}
        # Format the path pattern
        path = self.pattern.format(**fargs)

        # Append nested route paths
        if name:
            name, dot, rest = name.partition('.')
            path += getattr(self, name).reverse(rest, **kwargs)
        elif kwargs:
            path = '{}?{}'.format(name, www.Query(kwargs))

        # Return the total path from this part to the end
        return path


    def resolve(self, path=None, **kwargs):
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
        rest = path[match.end():]

        # Look for a deeper match and return it if found
        for route in self._routes:
            deeper = route.resolve(rest)
            if deeper:
                endpoint, _kwargs = deeper
                kwargs.update(_kwargs)
                return endpoint, kwargs

        # Return the endpoint and the matched, processed kwargs
        return self.endpoint, kwargs

    def __str__(self):
        """
        Format the named pattern groups and return the full pattern.
        """
        return self.pattern.format(**{ k: '(?P<{}>{})'.format(k, v)
                for k, v in self._parts.items()})

