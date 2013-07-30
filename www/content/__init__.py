from .negotiate import TYPES, MIMES, content_type, accept_type
from . import serializers
from . import deserializers

def serialize(data, type, **kwargs):
    type = MIMES.get(type, type)
    return getattr(serializers, type)(data, **kwargs)

def deserialize(data, type, **kwargs):
    type = MIMES.get(type, type)
    return getattr(deserializers, type)(data, **kwargs)

