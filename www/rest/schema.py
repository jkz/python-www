"""
Schemas facilitate data marshaling. In this case meaning:
transforming input data to output data and vice versa.
"""
from . import exceptions

class Validator:
    message = ''

    def run(self, value):
        return

    def __call__(self):
        pass


class Member:
    """
    The interface of fields and schemas.
    """
    def input(self, value):
        """
        Return the output version for given input.
        """
        raise NotImplementedError

    def output(self, value):
        """
        Return the input version for given output.
        """
        raise NotImplementedError

    def meta(self):
        """
        Returns a dictionary of meta information of the member.
        """
        raise NotImplementedError

class Identity:
    def input(self, value):
        return value

    def output(self, value):
        return value

    def meta(self):
        return {'info': "Input and output are identical"}


class Field(Member):
    primitive = 'string'

    default = None
    nullable = False
    required = True
    writable = False
    readable = True

    empty = (None, (), [], {})

    info = ''
    choices = None

    validators = ()

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    #XXX This initalization is thread unsafe and implies that
    #    field instances be used by one schema at most.
    #XXX Fields might even not need to know their parent (schema)
    def initialize(self, parent):
        self.parent = parent

    def value(self, value):
        return value

    def input(self, value):
        return self.value(value)

    def output(self, value):
        return self.value(value)

    def validate(self, value):
        if value in self.empty:
            if not self.nullable:
                raise exceptions.Missing

            if not self.required:
                raise exceptions.Omitted

        if self.choices and not value in self.choices:
            raise exceptions.ValidationError('{} not in {}'.format(value,
                    self.choices)


    def run_validators(self, value):
        if value in self.empty:
            return

        messages = []

        for validator in self.validators:
            try:
                validator(value)
            except exceptions.ValidationError as e:
                messages.append(e.messages)  #TODO: proper error messages

        if messages:
            raise exceptions.ValidationError(messages)


    def parse(self, value):
        value = self.input(value)
        self.validate(value)
        self.run_validators(value)
        return value

    def meta(self):
        meta = {}
        meta['info'] = self.info or self.__doc__
        meta['nullable'] = self.nullable
        meta['required'] = self.required
        meta['primitive'] = self.primitive
        #meta['type'] = self.type
        meta['readable'] = self.readable
        meta['writable'] = self.writable
        if self.default is not None:
            meta['default'] = self.default
        if self.choices:
            meta['choices'] = self.choices
        return meta



class Bool(Field):
    """A value representing True or False"""

    primitive = 'boolean'

    truthy = ('true', 'True', 't', 'yes', 'y', '1')
    falsy = ('false', 'False', 'f', 'no', 'n', '0')

    def input(self, value):
        if value in self.truthy:
            return True
        if value in self.falsy:
            return False
        return bool(value)

    def meta(self):
        meta = super().meta()
        #schema['truthy'] = truthy
        #schema['falsy'] = truthy
        return meta

class Number(Field):
    """A numeric value"""

    primitive = 'number'

    min = None
    max = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.min is not None:
            self.validators += (lambda x: x >= self.min,)
        if self.max is not None:
            self.validators += (lambda x: x <= self.max,)

    def meta(self):
        meta = super().meta()
        if self.min is not None:
            meta['min'] = self.min
        if self.max is not None:
            meta['max'] = self.max
        return meta


class Integer(Number):
    """A numeric value without decimals"""

    primitive = 'integer'

    def value(self, value):
        return int(value)

class Decimal(Number):
    decimals = None

class Float(Number):
    def value(self, value):
        return float(value)

class String(Field):
    """A sequence of characters."""

    length = None
    min_length = None
    max_length = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.length is not None:
            self.min_length = self.length
            self.max_length = self.length
        if self.min_length is not None:
            self.validators += (lambda x: len(x) >= self.min_length,)
        if self.max_length is not None:
            self.validators += (lambda x: len(x) <= self.max_length,)

    def value(self, value):
        return str(value)


class Tuple(Field):
    fields = ()

    @property
    def primitive(self):
        return '({}) tuple'.format(', '.join(f.primitive for f in self.fields))

    def __init__(self, *fields, **kwargs):
        super().__init__(**kwargs)
        self.fields = fields

    def value(self, value):
        return tuple(f.value(value) for f in self.fields)

    def input(self, value):
        return tuple(f.input(value) for f in self.fields)

    def output(self, value):
        return tuple(f.output(value) for f in self.fields)

    def meta(self):
        meta = super().meta()
        meta['fields'] = tuple(f.meta() for f in self.fields)
        return meta

class Array(Field):
    field = Field()

    def __init__(self, field, *args, **kwargs):
        super().__init__(**kwargs)
        self.field = field

    @property
    def primitive(self):
        return self.field.primitive + ' array'

    def value(self, value):
        return [self.field.value(v) for v in value]

    def input(self, value):
        return [self.field.input(v) for v in value]

    def output(self, value):
        return [self.field.output(v) for v in value]

class Object(Field):
    primitive = 'object'
    writable = False
    schema = None

    def __init__(self, schema, *args, **kwargs):
        self.schema = schema
        return super().__init__(self, *args, **kwargs)

    def value(self, value):
        if self.schema:
            return self.schema.input(value)
        return value

    def input(self, value):
        if self.schema:
            return self.schema.input(value)
        return value

    def output(self, value):
        if self.schema:
            return self.schema.output(value)
        return value

    def meta(self):
        return self.schema.meta()



class Creater(Field):
    accessor = ''

    def value(self, value):
        pass

class Reader(Creater):
    readable = True

class Writer(Creater):
    readable = False

class Date(Field):
    pass
class Time(Field):
    pass
class DateTime(Field):
    pass


class Schema(dict, Member):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in kwargs.values():
            field.initialize(self)

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

    #def extract(self, data, *key):
    def extract(self, data, key, required=True):
        if callable(data):
            return data(key)
        if key is None:
            return data
        if isinstance(data, dict):
            return data[key]
        else:
            return getattr(data, key)
        assert False

    def extract_input(self, data, key=None):
        return self.extract(data, key)

    def extract_output(self, data, key=None):
        return self.extract(data, key)

    def input(self, data):
        input = {}
        for name, field in self.writables():
            alias = getattr(field, 'alias', name)
            extract = self.extract_input(data, name)
            try:
                input[alias] = field.parse(extract)
            except exceptions.Omitted:
                continue
        return input

    def output(self, data):
        output = {}
        for name, field in self.readables():
            alias = getattr(field, 'alias', name)
            extract = self.extract_output(data, alias)
            try:
                output[name] = field.output(extract)
            except exceptions.Omitted:
                continue
        return output

    def meta(self):
        return {name : field.meta() for name, field in self.items()}



class TupleSchema(tuple, Member):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self:
            field.initialize(self)

    def __add__(self, other):
        if not isinstance(other, Schema):
            raise TypeError
        return self.__class__(self) + other

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

    def extract(self, data, *key):
        if callable(data):
            return data(key)
        if key is None:
            return data
        if isinstance(data, dict):
            return data.get(key)
        else:
            return getattr(data, key)

    def extract_input(self, data, key=None):
        return self.extract(data, key)

    def extract_output(self, data, key=None):
        return self.extract(data, key)

    def input(self, data):
        input = []
        for value, field in zip(data, self.writables()):
            alias = getattr(field, 'alias', None)
            extract = self.extract_input(data, alias)
            try:
                input.append(field.parse(extract))
            except exceptions.Omitted:
                input.append(extract)
        return input

    def output(self, data):
        output = []
        for name, field in self.readables():
            alias = getattr(field, 'alias', name)
            extract = self.extract_output(data, alias)
            try:
                output[name] = field.output(extract)
            except exceptions.Omitted:
                continue
        return output

    def meta(self):
        return {name : field.meta() for name, field in self.items()}

