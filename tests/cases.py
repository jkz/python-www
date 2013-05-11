import functools
import time
import unittest

import www

class TestResource(unittest.TestCase):
    def test_basic(self):
        result = www.Resource('//example.com/foo/', kitten='fluffy').url
        expected = 'http://example.com/foo/?kitten=fluffy'
        self.assertEqual(result, expected)

class TestRequest(unittest.TestCase):
    def test_basic(self):
        result = www.Request('//example.com/foo/', kitten='fluffy').params
        expected = ('GET', '/foo/?kitten=fluffy', None, {'User-Agent': www.USER_AGENT})
        self.assertEqual(result, expected)

class TestConnection(unittest.TestCase):
    def test_basic(self):
        conn = www.Connection('example.com', username='jess')
        request = conn.build_request('/foo/', method='get')
        result = str(request)
        expected = 'GET http://jess@example.com/foo/'
        self.assertEqual(result, expected)
