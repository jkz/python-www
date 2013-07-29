import www

from www.utils.decorators import cached_property

from .. import exceptions

# Maps all convertor names to mime types
TYPES = {
    'text': 'text/plain',
    'json': 'application/json',
    'jsonp': 'application/javascript',
    'form': 'application/x-www-form-urlencoded',
    'xml': 'application/xml',
    'mp3': 'audio/mpeg',
    'bytes': 'application/octet-stream',
}

# Maps all mime types to convertor names
MIMES = {
    'text/plain': 'text',
    'application/json': 'json',
    'application/x-www-form-urlencoded': 'form',
    'application/xml': 'xml',
    'audio/mpeg': 'mp3',
    'application/octet-stream': 'bytes',
}

def mime_list(types):
    """
    Return a list of convertors prepared for mimeparse.best_match
    """
    for type in reversed(types):
        yield MIMES.get(type, type)

def accept_type(allowed, header):
    match = mimeparse.best_match(mime_list(allowed), header)
    type = TYPES.get(match)
    if type not in allowed:
        raise exceptions.NotAcceptable(header)
    return type

def content_type(allowed, header):
    #see http://www.ietf.org/rfc/rfc2616.txt section 7.2.1
    #type = TYPES.get(header, 'application/octet-stream')
    type = TYPES.get(header)
    if type not in allowed:
        raise exceptions.UnsupportedMediaType(header)
    return type

