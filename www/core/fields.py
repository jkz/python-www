from . import exceptions
from . import validators

class Field:
    """
    A field is a description of a data attribute. It supports a convert
    method for changing external to internal values, and revert for the
    opposite.

    Inward data should be passed to resolve, where it will be converted and
    validated.
    Outward data, passed to reverse is considered valid and just needs
    reversion.
    """
    #XXX inspired by JSON
    # The datatype of the field
    primitive = 'string'

    # Alias is used to find the fields' respective value on a data object.
    # It has 5 modes:
    # - <str>: the name of the field on an object
    # - <int>: the index on a given tuple
    # - True: the accessor configured for the calling context
    # - False: pass the entire object
    # - None: do not pass anything at all
    alias = True

    # The value used when not given
    # Exceptions are automatically raised
    default = exceptions.Omitted

    # A tuple of values allowed
    choices = None

    # Tuple of values matching the empty value for the field
    nulls = (None, (), [], {}, '', set())

    # Flags whether this field allows empty values
    nullable = False

    # Flags whether this field requires a value
    #XXX takes precedence over default when it is Omitted
    required = True

    # A user friendly description of the field
    help_text = 'This is a field'

    # A tuple of callables which are all passed the value to validate
    validators = ()

    #TODO pick sane defaults
    readable = True
    writable = True

    def __init__(self, **kwargs):
        _validators = kwargs.pop('validators', False)
        if _validators:
            self.validators += _validators

        self.__dict__.update(kwargs)

    @property
    def null(self):
        return self.nulls[0]

    def get_default(self):
        try:
            raise self.default
        except exceptions.Omitted:
            if self.nullable:
                return None
            if self.required:
                raise exceptions.Missing
            raise
        except TypeError:
            return self.default

    def accessor(self, name):
        if self.alias is True:
            return name
        elif self.alias is False:
            return None
        else:
            return self.alias

    def extract(self, object, key=None):
        if key is not None:
            try:
                if hasattr(object, '__getitem__'):
                    return object[key]
                else:
                    return getattr(object, key)
            except (IndexError, KeyError, AttributeError):
                return self.get_default()

        return object

    def convert(self, value):
        """Return internal representation of value"""
        return value

    def revert(self, value):
        """Return external representation of value"""
        return value

    def validate(self, value):
        if value in self.nulls:
            if not self.nullable:
                raise exceptions.Invalid('Not nullable')
            return

        if self.choices and not value in self.choices:
            raise exceptions.Invalid('{} not in {}'.format(value,
                    self.choices))

        validators.run_validators(self.validators, value)

    def resolve(self, value):
        #XXX Any null value converts to None here, this decision is not final
        if value in self.nulls:
            value = None
        else:
            value = self.convert(value)
        self.validate(value)
        return value

    def reverse(self, value):
        if value is None:
            return self.null
        else:
            return self.revert(value)

    def meta(self):
        meta = {}
        meta['info'] = self.help_text or self.__doc__
        meta['nullable'] = self.nullable
        meta['required'] = self.required
        meta['primitive'] = self.primitive
        meta['readable'] = self.readable
        meta['writable'] = self.writable
        if self.default is not exceptions.Omitted:
            meta['default'] = self.default
        if self.choices:
            meta['choices'] = self.choices
        return meta


class Boolean(Field):
    """A value representing True or False"""

    primitive = 'boolean'

    truthy = (True, 'true', 'True', 't', 'yes', 'y', '1')
    falsy = (False, 'false', 'False', 'f', 'no', 'n', '0')

    def convert(self, value):
        if value in self.truthy:
            return True
        if value in self.falsy:
            return False
        return bool(value)

    def revert(self, value):
        #XXX Maybe special case None?
        if value:
            return self.truthy[0]
        else:
            return self.falsy[0]

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.min is not None:
            self.validators += validators.Min(self.min),
        if self.max is not None:
            self.validators += validators.Max(self.max),

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.length is not None:
            self.validators += (validators.Length(self.length),)
        else:
            if self.min_length is not None:
                self.validators += (validators.MinLength(self.min_length),)
            if self.max_length is not None:
                self.validators += (validators.MaxLength(self.max_length),)

    def convert(self, value):
        return str(value)


class Date(Field):
    pass

class Time(Field):
    pass

class DateTime(Field):
    pass

class Tuple(Field):
    fields = ()

    @property
    def primitive(self):
        return 'tuple of ({})'.format(', '.join(f.primitive for f in self.fields))

    def __init__(self, *fields, **kwargs):
        super().__init__(**kwargs)
        self.fields = fields

    def convert(self, value):
        return tuple(f.convert(value) for f in self.fields)

    def revert(self, value):
        return tuple(f.revert(value) for f in self.fields)

    def meta(self):
        meta = super().meta()
        meta['fields'] = tuple(f.meta() for f in self.fields)
        return meta

class Array(Field):
    field = Field()

    def __init__(self, field, **kwargs):
        super().__init__(**kwargs)
        self.field = field

    @property
    def primitive(self):
        return 'array of ({})'.format(self.field.primitive)

    def convert(self, value):
        return [self.field.convert(v) for v in value]

    def revert(self, value):
        return [self.field.revert(v) for v in value]

    def meta(self):
        meta = super().meta()
        meta['field'] = self.field.meta()
        return meta

class Object(Field):
    primitive = 'object'
    writable = False
    schema = None

    def __init__(self, schema, **kwargs):
        self.schema = schema
        return super().__init__(**kwargs)

    def convert(self, value):
        if self.schema:
            return self.schema.convert(value)
        return value

    def revert(self, value):
        if self.schema:
            return self.schema.resolve(value)
        return value

    def meta(self):
        if self.schema:
            return self.schema.meta()
        return super().meta()

