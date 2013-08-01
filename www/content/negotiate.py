from . import mimeparse
from . import TYPES, MIMES

def iter_mimes(types):
    """
    Return a list of convertors prepared for mimeparse.best_match
    """
    for type in reversed(types):
        for mimes in TYPES.get(type, list(type)):
            for mime in mimes:
                yield mime

def type(allowed, type):
    """
    Negotiate a media-type value.
    """
    type = MIMES.get(type, type)
    if type in allowed:
        return type
    #raise exceptions.UnsupportedMediaType(header)

def range(allowed, range):
    """
    Negotiate a media-range header.
    """
    match = mimeparse.best_match(iter_mimes(allowed), TYPES.get(range, range))
    return type(allowed, match)
    #raise exceptions.NotAcceptable(header)



