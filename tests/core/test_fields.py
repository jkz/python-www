import unittest

from www.core import exceptions
from www.core import options
from www.core import fields

class Option(options.Option):
    order = ('as_dict', 'as_attr')
    containers = dict(
        as_dict = lambda self, obj, key: obj.dict[key],
        as_attr = lambda self, obj, key: getattr(obj, key),
    )

class TestField(unittest.TestCase):
    def test_basic(self):
        field = fields.Integer(
            min = 10,
            max = 100,
            default = 50,
        )

        self.assertEqual(field.resolve('10'), 10)
        self.assertEqual(field.resolve('100'), 100)
        self.assertRaises(exceptions.Invalid, field.resolve, '9')
        self.assertRaises(exceptions.Invalid, field.resolve, '101')

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

        self.assertEqual(field.resolve('a'), 'a')
        self.assertRaises(exceptions.Invalid, field.resolve, 'd')

    def test_default(self):
        field = fields.String(
            default = 'default',
        )

        test = ['first', 'second']

        self.assertEqual(field.extract(test, 0), 'first')
        self.assertEqual(field.extract(test, 1), 'second')
        self.assertEqual(field.extract(test, 2), 'default')

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
            self.assertEqual(nullable.resolve(null), None)

        notnullable = fields.Field(
            nullable = False,
        )

        for null in nulls:
            self.assertRaises(exceptions.Invalid, notnullable.resolve, null)

    def test_meta(self):
        pass


