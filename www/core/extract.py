"""
The classes in this module describe how to extract values from data.
"""
from . import exceptions

class Extractor:
    def __init__(self, param, **options):
        self.param = param
        self.__dict__.update(options)

    def __call__(self, data):
        try:
            return self.extract(data)
        except (AttributeError, KeyError):
            raise exceptions.Missing

class Call(Extractor):
    def extract(self, data):
        return self.param(data)

class Attr(Extractor):
    def extract(self, data):
        return getattr(data, self.param)

class Key(Extractor):
    def extract(self, data):
        return data[self.param]

class All(Extractor):
    def extract(self, data):
        if callable(data):
            return data(self.param)
        if self.param is None:
            return data
        if hasattr(data, '__getitem__'):
            return data[self.param]
        else:
            return getattr(data, self.param)
