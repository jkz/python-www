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
    if hasattr(data, '__getitem__'):
        return data[key]
    else:
        return getattr(data, key)

class Schema:
    #TODO immutable
    def __add__(self, other):
        """Combine two schemas into a new one"""
        raise NotImplementedError

    def extract_input(self, field, data, key=None):
        return extract(data, key)

    def extract_output(self, field, data, key=None):
        return field.extract(data, key)


class Object(dict, Schema):
    def __add__(self, other):
        if not isinstance(other, Object):
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

    def convert(self, data):
        input = {}
        for name, field in self.writables():
            key = field.accessor(name)
            value = self.extract_input(field, data, name)
            try:
                input[key] = field.parse(value)
            except exceptions.Omitted:
                continue
        return input

    def revert(self, data):
        output = {}
        for name, field in self.readables():
            key = field.accessor(name)
            value = self.extract_output(field, data, key)
            try:
                output[name] = field.revert(value)
            except exceptions.Omitted:
                continue
        return output

    def meta(self):
        return {name : field.meta() for name, field in self.items()}



class Tuple(tuple, Schema):
    def __add__(self, other):
        if not isinstance(other, Tuple):
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

    def convert(self, data):
        input = []
        for data, field in zip(data, self.writables()):
            value = self.extract_input(data)
            try:
                input.append(field.parse(value))
            except exceptions.Omitted:
                input.append(value)
        return tuple(input)

    def revert(self, data):
        output = []
        for data, field in zip(data, self.readables()):
            value = self.extract_output(field, data)
            try:
                output.append(field.revert(value))
            except exceptions.Omitted:
                output.append(value)
        return tuple(output)

    def meta(self):
        return tuple(field.meta() for field in self)

