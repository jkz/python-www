from . import exceptions
from . import validators

class Value:
    primitive = 'string'

    default = None
    nullable = False
    required = True

    nulls = (None, (), [], {}, '')

    info = ''
    choices = None

    validators = ()

    def __init__(self, **kwargs):
        validators = conf.pop('validators')
        if validators:
            self.validators += validators
        self.__dict__.update(conf)

    def convert(self, value):
        return value

    def validate(self, value):
        if value in self.nulls:
            if not self.nullable:
                raise exceptions.Missing

            if not self.required:
                raise exceptions.Omitted

        if self.choices and not value in self.choices:
            raise exceptions.ValidationError('{} not in {}'.format(value,
                    self.choices)


    def parse(self, value):
        value = self.input(value)
        self.validate(value)
        validators.run_validators(self.validators, value)
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

    def convert(self, value):
        if value in self.truthy:
            return True
        if value in self.falsy:
            return False
        return bool(value)

    def meta(self):
        meta = super().meta()
        meta['truthy'] = truthy
        meta['falsy'] = truthy
        return meta

class Number(Field):
    """A numeric value"""

    primitive = 'number'

    min = None
    max = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.min is not None:
            self.validators += validators.Min(self.min)
        if self.max is not None:
            self.validators += validators.Max(self.max)

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

    def convert(self, value):
        return int(value)

class Decimal(Number):
    decimals = None

class Float(Number):
    def convert(self, value):
        return float(value)

class String(Field):
    """A sequence of characters."""

    length = None
    min_length = None
    max_length = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.length is not None:
            self.validators += (validators.Length(self.length),)
        else:
            if self.min_length is not None:
                self.validators += (validators.MinLength(self.min_length),)
            if self.max_length is not None:
                self.validators += (validators.MaxLength(self.max_length),)

    def convert(self, value):
        return str(value)

