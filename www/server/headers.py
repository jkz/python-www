"""
An implementation with some compliance for
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
"""
import www

from . import structures

class Header(dict, structures.NestedClass):
    def pretty(self):
        return {self.prettify(key) : val for key, val in self.items()}

    def uglify(self, key):
        if not key.startswith('HTTP_'):
            key = 'HTTP_' + key
        return key.replace('-', '_').upper()

    def prettify(self, key):
        if key.startswith('HTTP_'):
            key = key[5:]
        return '-'.join(s.capitalize() for s in key.lower().split('_'))

    def __delitem__(self, key):
        super().__delitem__(self.uglify(key))

    def __getitem__(self, key):
        return super().__getitem__(self.uglify(key))

    def __setitem__(self, key, val):
        super().__setitem__(self.uglify(key), val)

    def update(self, other):
        for key, val in other.items():
            self[key] = val

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

    def accept_charset(self, ):
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

    def authorization(self, creds):
        pass

    def cache_control(self,
        pass
