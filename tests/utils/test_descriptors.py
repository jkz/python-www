import unittest

from www.utils import descriptors

class TestBindablePartial(unittest.TestCase):
    def test_bindable_partial(self):
        def method(*args, **kwargs):
            return args, kwargs

        class Class:
            pass

        unbound = descriptors.BindablePartial(
            method,
            'arg1',
            kwarg1 = True
        )

        args, kwargs = unbound('arg2', kwarg2=True)

        self.assertEqual(unbound.__name__, 'method')
        self.assertEqual(args, ('arg1', 'arg2'))
        self.assertEqual(kwargs, {'kwarg1': True, 'kwarg2': True})

        Class.bound = descriptors.BindablePartial(
            method,
            'arg1',
            kwarg1 = True
        )

        obj = Class()

        args, kwargs = obj.bound('arg2', kwarg2=True)

        self.assertEqual(obj.bound.__name__, 'method')
        self.assertEqual(args, (obj, 'arg1', 'arg2'))
        self.assertEqual(kwargs, {'kwarg1': True, 'kwarg2': True})
