import unittest
from www.core import sexy
from www.core import exceptions

class TestMethod(unittest.TestCase):
    def test_basic(self):
        class Test:
            method = sexy.Method()

        t = Test()

        self.assertEqual(t.method, None)
        t.method = 'get'
        self.assertEqual(t.method, 'GET')
        self.assertRaises(exceptions.MethodNotAllowed, lambda: setattr(t, 'method', 'INVALID'))


class TestRequest(unittest.TestCase):
    def test_basic(self):
        result = sexy.Request('//example.com/foo/', kitten='fluffy').split()
        expected = ('GET', '/foo/?kitten=fluffy', None, {})
        self.assertEqual(result, expected)

class TestAuthority(unittest.TestCase):
    def test_basic(self):
        for a in [
            sexy.Authority('example.com'),
            sexy.Authority('example.com/ignore'),
            sexy.Authority('example.com:80'),
            sexy.Authority('http://example.com'),
            sexy.Authority('http://example.com:80'),
            sexy.Authority(scheme='http', host='example.com', port=80),
            sexy.Authority('wrong.com:80', host='example.com'),
            sexy.Authority('example.com:81', port=80),
            sexy.Authority('https://example.com', scheme='http'),
        ]:
            self.assertEqual(str(a), 'http://example.com')

        boob = sexy.Authority(scheme='boob', host='boob', port=8008)
        self.assertEqual(str(boob), 'boob://boob:8008')
        self.assertEqual(str(sexy.Authority()), 'http://')

class TestResource(unittest.TestCase):
    def test_basic(self):
        result = sexy.Resource('//example.com/foo/', kitten='fluffy').url
        expected = 'http://example.com/foo/?kitten=fluffy'
        self.assertEqual(result, expected)


