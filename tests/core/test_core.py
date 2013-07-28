import unittest

from www.core import exceptions
from www.core import validators
from www.core import fields
from www.core import options
from www.core import schema

E = exceptions.ValidationError
v = validators

class Option(options.Option):
    order = ('as_dict', 'as_attr')
    containers = dict(
        as_dict = lambda self, obj, key: obj.dict[key],
        as_attr = lambda self, obj, key: getattr(obj, key),
    )

class TestValidator(unittest.TestCase):
    def test_basic(self):

        eq = v.Validator(True)
        eq(True)
        self.assertRaises(E, eq, False)

        min = v.Min(10)
        min(11)
        self.assertRaises(E, min, 9)

        max = v.Max(10)
        max(9)
        self.assertRaises(E, max, 11)

        len = v.Length(4)
        len('poop')
        self.assertRaises(E, len, 'poops')

        minlen = v.MinLength(4)
        minlen('poop')
        self.assertRaises(E, minlen, 'poo')

        maxlen = v.MaxLength(4)
        maxlen('poop')
        self.assertRaises(E, maxlen, 'poops')

        vldtrs = [len, minlen, maxlen]
        v.run_validators(vldtrs, 'poop')
        self.assertRaises(E, v.run_validators, vldtrs, 'poops')

class TestField(unittest.TestCase):
    def test_basic(self):
        field = fields.Integer(
            min = 10,
            max = 100,
            default = 50,
        )

        self.assertEqual(field.parse('10'), 10)
        self.assertEqual(field.parse('100'), 100)
        self.assertRaises(exceptions.ValidationError, field.parse, '9')
        self.assertRaises(exceptions.ValidationError, field.parse, '101')

    def test_alias(self):
        as_str = fields.Boolean(
            alias = 'alias',
        )
        as_int = fields.Boolean(
            alias = 1,
        )
        as_true = fields.Boolean(
            alias = True,
        )
        as_false = fields.Boolean(
            alias = False,
        )


        class Object:
            alias = True
            key = False

        for field, obj in [
            (as_str, Object()),
            (as_str, {'alias': True}),
            (as_int, [False, True]),
            (as_true, {'alias': False, 'key': True}),
            (as_false, True),
        ]:
            self.assertEqual(field.extract(obj, field.accessor('key')), True)


    def test_choices(self):
        field = fields.String(
            choices = ['a', 'b', 'c'],
        )

        self.assertEqual(field.parse('a'), 'a')
        self.assertRaises(E, field.parse, 'd')

    def test_default(self):
        field = fields.String(
            default = 'poop',
        )

        test = ['first', 'second']

        self.assertEqual(field.extract(test, 0), 'first')
        self.assertEqual(field.extract(test, 1), 'second')
        self.assertEqual(field.extract(test, 2), 'poop')

        omitter = fields.String(required=False)
        misser = fields.String(required=True)

        self.assertRaises(exceptions.Omitted, omitter.extract, test, 2)
        self.assertRaises(exceptions.Missing, misser.extract, test, 2)

    def test_nulls(self):
        nullable = fields.Field(
            nullable = True,
        )

        nulls = (None, (), [], {}, '', set())

        for null in nulls:
            self.assertEqual(nullable.parse(null), None)

        notnullable = fields.Field(
            nullable = False,
        )

        for null in nulls:
            self.assertRaises(E, notnullable.parse, null)

    def test_meta(self):
        pass


class TestOption(unittest.TestCase):
    def test_basic(self):
        option = Option(
            as_dict = 'key',
            as_attr = 'attr',
            field = fields.String(
                default = 'DEFAULT',
            )
        )

        class TestObject:
            dict = {}


        obj = TestObject()
        self.assertEqual(option.parse(obj), 'DEFAULT')
        obj.attr = 'ATTR'
        self.assertEqual(option.parse(obj), 'ATTR')
        obj.dict['key'] = 'KEY'
        self.assertEqual(option.parse(obj), 'KEY')

class Href(fields.Field):
    writable = False

    def revert(self, val):
        return '/users/{}'.format(val['id'])

class SchemaTestCase(unittest.TestCase):
    def test_schema(self):
        thing = schema.Object(
            id = fields.Integer(writable=True),
            name = fields.String(writable=True),
            href = Href(alias=False),
        )

        person = thing + schema.Object(
            friends = fields.Array(
                Href(),
                writable = False,
            ),
        )

        quote = thing + schema.Object(
            text = fields.String(writable=True),
            person = fields.Object(person),
        )

        sam = {
            'id': 1,
            'name': 'Sam',
            'friends': [],
        }

        frodo = {
            'id': 2,
            'name': 'Frodo',
            'friends': [sam],
        }

        smeagol = {
            'id': 3,
            'name': 'Smeagol',
            'friends': [sam, frodo],
        }

        sorry = {
            'id': 10,
            'name': 'Sorry',
            'person': sam,
            'text': 'Sorry mister Frodo',
        }

        tricksed = {
            'id': 11,
            'name': 'Tricksed',
            'person': smeagol,
            'text': 'Tricksed us?!',
        }

        print(person.convert(sam))
        print(person.convert(frodo))
        print(person.convert(smeagol))

        print(person.revert(sam))
        print(person.revert(frodo))
        print(person.revert(smeagol))

        print(quote.convert(sorry))
        print(quote.convert(tricksed))

        print(quote.revert(sorry))
        print(quote.revert(tricksed))


