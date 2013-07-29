"""
Schemas facilitate data marshaling. In this case meaning:
transforming input data to output data and vice versa.

A schema is a collection of fields with names. Schemas can be
nested by fields.
"""
from . import exceptions

class Schema:
    #TODO make immutable? S.Lott says we should not attempt to do that


    def __add__(self, other):
        """Combine two schemas into a new one"""
        raise NotImplementedError

    def extract(self, data, key, required=True):
        if callable(key):
            return key(data)
        if key is None:
            return data
        if hasattr(data, '__getitem__'):
            return data[key]
        else:
            return getattr(data, key)


class Object(dict, Schema):
    def __add__(self, other):
        """
        Combine two object schemas. The right side takes precedence over
        the left.
        """
        if not isinstance(other, Object):
            raise TypeError
        new = self.__class__(self)
        new.update(other)
        return new

    def __radd__(self, other):
        return self + other

    def writables(self):
        """Yield all (name, field) pairs with fields that are writable"""
        for name, field in self.items():
            if field.writable:
                yield name, field

    def readables(self):
        """Yield all (name, field) pairs with fields that are readable"""
        for name, field in self.items():
            if field.readable:
                yield name, field

    def resolve(self, data):
        """
        Take all writable fields and build a structure from given input
        data with the fields.
        """
        input = {}
        for name, field in self.writables():
            key = field.accessor(name)
            value = self.extract(data, name)
            try:
                input[key] = field.resolve(value)
            except exceptions.Omitted:
                continue
        return input

    def reverse(self, data):
        """
        Take all readable fields and build a structure from given output.
        """
        output = {}
        for name, field in self.readables():
            key = field.accessor(name)
            value = field.extract(data, key)
            try:
                output[name] = field.reverse(value)
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
        for index, field in enumerate(self):
            if field.writable:
                yield index, field

    def readables(self):
        for index, field in enumerate(self):
            if field.readable:
                yield index, field

    def resolve(self, data):
        input = []
        for index, field in self.writables():
            key = field.accessor(index)
            value = self.extract(data, key)
            try:
                input.append(field.resolve(value))
            except exceptions.Omitted:
                input.append(value)
        return tuple(input)

    def reverse(self, data):
        output = []
        for index, field in enumerate(self.readables()):
            key = field.accessor(index)
            value = field.extract(data, key)
            try:
                output.append(field.reverse(value))
            except exceptions.Omitted:
                output.append(value)
        return tuple(output)

    def meta(self):
        return tuple(field.meta() for field in self)

