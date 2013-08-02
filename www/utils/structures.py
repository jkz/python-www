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
        print('mapping', mapping)
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
                yield key, vals[0]

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
            self.add(key, value)


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

