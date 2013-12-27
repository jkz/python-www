import unittest

from www.core import options
from www.core import fields

class Option(options.Option):
    order = ('dict', 'attr')
    containers = dict(
        dict = lambda self, obj, key: (print('dict', obj, key) or obj.dict[key]),
        attr = lambda self, obj, key: (print('attr', obj, key) or getattr(obj, key)),
    )

class TestOption(unittest.TestCase):
    def test_options(self):
        option = Option(
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

