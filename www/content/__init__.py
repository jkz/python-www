from www.utils.structures import MultiDict

from . import serializers
from . import deserializers

TYPES = MultiDict((
    ('text',  ['text/plain']),
    ('json',  ['application/json']),
    ('jsonp', ['application/javascript']),
    ('form',  ['application/x-www-form-urlencoded']),
    ('xml',   ['application/xml', 'text/xml']),
    ('mp3',   ['audio/mpeg']),
    ('bytes', ['application/octet-stream']),
))

# Maps all mime types to convertor names
MIMES = {
    'text/plain': 'text',
    'application/json': 'json',
    'application/x-www-form-urlencoded': 'form',
    'application/xml': 'xml',
    'text/xml': 'xml',
    'audio/mpeg': 'mp3',
    'application/octet-stream': 'bytes',
}

def serialize(data, type, **kwargs):
    type = MIMES.get(type, type)
    return getattr(serializers, type)(data, **kwargs)

def deserialize(data, type, **kwargs):
    type = MIMES.get(type, type)
    return getattr(deserializers, type)(data, **kwargs)

