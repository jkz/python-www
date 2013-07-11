error = 'XXX'

def multi_items(mapping):
    if isinstance(mapping, MultiDict):
        for item in mapping.items(multi=True):
            yield item
    elif isinstance(mapping, dict):
        for key, value in mapping.items():
            if isinstance(value, (tuple, list)):
                for value in value:
                    yield key, value
            else:
                yield key, value
    else:
        for item in mapping:
            yield item


class MultiDict(dict):
    """
    This dictionary stores all values in lists under their keys. When used
    normally, the first item in the list is used. To access all values, there
    are several methods.
    """
    def __init__(self, mapping=None):
        if isinstance(mapping, MultiDict):
            super().__init__({k: L[:] for k, L in mapping.lists()})
        elif isinstance(mapping, dict):
            super().__init__({k: [v] for k, v in mapping.items()})
        else:
            super().__init__({k: [v] for k, v in mapping or ()})

    def __getstate__(self):
        return dict(self.lists())

    def __setstate__(self, value):
        dict.clear(self)
        dict.update(self, value)

    def __getitem__(self, key):
        return super().__getitem__(key)[0]

    def __setitem__(self, key, val):
        super().__setitem__(key, [val])

    def add(self, key, value):
        super().setdefault(key, []).append(value)

    def items(self, multi=False):
        for key, vals in dict.items(self):
            if multi:
                for val in vals:
                    yield key, val
            else:
                yield key, val[0]

    def lists(self):
        for key, val in dict.items(self):
            yield key, list(val)

    def getlist(self, key):
        try:
            return list(super().__getitem__(key))
        except KeyError:
            return []

    def listvalues(self):
        return dict.items(self)

    def values(self):
        for val in dict.values(self):
            yield(val[0])

    def copy(self):
        """Return a shallow copy of the multidict"""
        return self.__class__(self)

    def to_dict(self, multi=False):
        if multi:
            return dict(self.items())
        return dict(self.lists())

    def update(self, other_dict):
        """update() extends rather than replaces existing key lists."""
        for key, value in multi_items(other_dict):
            self.add(self, key, value)


class NormalizedKeysMixin:
    def _normalize_key(self, key):
        return key

    def __getattr__(self, key):
        return super().__getattr__(self._normalize(key))

    def __setattr__(self, key, val):
        super().__setattr__(self._normalize(key), val)

    def __delattr__(self, key):
        super().__delattr__(self._normalize(key))

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default


'''
class Header(
    MultiDict,
    NormalizedKeysMixin
):
    """
    Multivalue
    Normalized keys
    Special cases
        - Accept (mime tuples)
        - Content-Type (mime tuples)
        - Auth <auth type> params
        - Range (stuff)
    """
    def _normalize_key(self, key):
        return '-'.join(s.capitalize() for s in re.split(' |-', key.lower()))

    def accept(self, type, weight=1.0):
        pass

    def accept_encoding(self, type, weight=1.0):
        pass

    def accept_charset(...):
        pass

    def accept_encoding(...):
        pass

    def content_type(...):
        pass

    @automatic
    def content_length(...):
        pass

    def accept_ranges(...):
        pass

    def age(self, seconds):
        pass
'''

class Option(dict):
    def clean_default(self, default=error):
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

