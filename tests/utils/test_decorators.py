import unittest

from www.utils import decorators

class TestDefaultKwargs(unittest.TestCase):
    def test_default_kwargs(self):
        @decorators.default_kwargs(first=True, second=False)
        def alter_kwargs(first, second):
            return first, second

        self.assertEqual(alter_kwargs(), (True, False))
        self.assertEqual(alter_kwargs(first=False), (False, False))
        self.assertEqual(alter_kwargs(second=True), (True, True))


class TestCachedProperty(unittest.TestCase):
    def test_cached_property(self):
        class Class:
            value = 2

            @decorators.cached_property
            def prop(self):
                return obj.value * 2

        obj = Class()

        self.assertEqual(obj.prop, 4)
        obj.value = 8
        self.assertEqual(obj.prop, 4)

class TestLazyProperty(unittest.TestCase):
    def test_lazy_property(self):
        class Class:
            @decorators.lazy_property
            def prop(self):
                return {'key': True}

        self.assertEqual(Class.prop, None)

        obj = Class()
        val1 = obj.prop
        self.assertEqual(obj.prop, {'key': True})
        val2 = obj.prop
        self.assertEqual(val1 is val2, True)
