import unittest

from www.core import exceptions
from www.core import validators

E = exceptions.Invalid
v = validators

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
        len('good')
        self.assertRaises(E, len, 'invalid')

        minlen = v.MinLength(4)
        minlen('good')
        minlen('good too')
        self.assertRaises(E, minlen, 'bad')

        maxlen = v.MaxLength(4)
        maxlen('good')
        maxlen('ok')
        self.assertRaises(E, maxlen, 'invalid')

        vldtrs = [len, minlen, maxlen]
        v.run_validators(vldtrs, 'good')
        self.assertRaises(E, v.run_validators, vldtrs, 'invalid')

