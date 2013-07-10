"""
Schemas facilitate data marshaling. In this case meaning:
transforming input data to output data and vice versa.
"""
from . import exceptions

def extract(data, key, required=True):
    if callable(data):
        return data(key)
    if key is None:
        return data
    if isinstance(data, dict):
        return data[key]
    else:
        return getattr(data, key)
    assert False

class Object(dict):
    def __add__(self, other):
        if not isinstance(other, Schema):
            raise TypeError
        new = self.__class__(self)
        new.update(other)
        return new

    def __radd__(self, other):
        return self + other

    def writables(self):
        for name, field in self.items():
            if field.writable:
                yield name, field

    def readables(self):
        for name, field in self.items():
            if field.readable:
                yield name, field


    def extract_input(self, data, key=None):
        return extract(data, key)

    def extract_output(self, data, key=None):
        return extract(data, key)

    def convert(self, data):
        input = {}
        for name, field in self.writables():
            alias = field.alias if field.alias is not None else name
            value = self.extract_input(data, name)
            try:
                input[alias] = field.parse(extract)
            except exceptions.Omitted:
                continue
        return input

    def revert(self, data):
        output = {}
        for name, field in self.readables():
            alias = field.alias if field.alias is not None else name
            value = self.extract_output(data, alias)
            try:
                output[name] = field.revert(value)
            except exceptions.Omitted:
                continue
        return output

    def meta(self):
        return {name : field.meta() for name, field in self.items()}



class Tuple(tuple):
    def __add__(self, other):
        if not isinstance(other, TupleSchema):
            raise TypeError
        return self.__class__(tuple(self) + other)

    def __radd__(self, other):
        self.update(other)
        return self

    def writables(self):
        for field in self:
            if field.writable:
                yield field

    def readables(self):
        for field in self:
            if field.readable:
                yield field

    def extract_input(self, data, key=None):
        return extract(data, key)

    def extract_output(self, data, key=None):
        return extract(data, key)

    def convert(self, data):
        input = []
        for value, field in zip(data, self.writables()):
            alias = field.alias if field.alias is not None else name
            value = self.extract_input(data, alias)
            try:
                input.append(field.parse(value))
            except exceptions.Omitted:
                input.append(value)
        return input

    def revert(self, data):
        output = []
        for name, field in self.readables():
            alias = field.alias if field.alias is not None else name
            value = self.extract_output(data, alias)
            try:
                output.append(field.output(value))
            except exceptions.Omitted:
                output.append(value)
        return output

    def meta(self):
        return tuple(field.meta() for field in self)

