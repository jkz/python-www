import unittest
from www.core import http
from www.core import exceptions

class TestMethod(unittest.TestCase):
    def test_basic(self):
        class Test:
            method = http.Method()

        t = Test()

        self.assertEqual(t.method, None)
        t.method = 'get'
        self.assertEqual(t.method, 'GET')
        self.assertRaises(exceptions.MethodNotAllowed, lambda: setattr(t, 'method', 'INVALID'))


class TestRequest(unittest.TestCase):
    def test_basic(self):
        result = http.Request('//example.com/foo/', kitten='fluffy').split()
        expected = ('GET', '/foo/?kitten=fluffy', None, {})
        self.assertEqual(result, expected)

class TestAuthority(unittest.TestCase):
    def test_basic(self):
        for a in [
            http.Authority('example.com'),
            http.Authority('example.com/ignore'),
            http.Authority('example.com:80'),
            http.Authority('http://example.com'),
            http.Authority('http://example.com:80'),
            http.Authority(scheme='http', host='example.com', port=80),
            http.Authority('wrong.com:80', host='example.com'),
            http.Authority('example.com:81', port=80),
            http.Authority('https://example.com', scheme='http'),
        ]:
            self.assertEqual(str(a), 'http://example.com')

        boob = http.Authority(scheme='boob', host='boob', port=8008)
        self.assertEqual(str(boob), 'boob://boob:8008')
        self.assertEqual(str(http.Authority()), 'http://')

class TestResource(unittest.TestCase):
    def test_basic(self):
        result = http.Resource('//example.com/foo/', kitten='fluffy').url
        expected = 'http://example.com/foo/?kitten=fluffy'
        self.assertEqual(result, expected)


