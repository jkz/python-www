from . import serializers
from . import deserializers

def serialize(data, type, **kwargs):
    return getattr(serializers, type)(data, **kwargs)

def deserialize(data, type, **kwargs):
    return getattr(deserializers, type)(data, **kwargs)

