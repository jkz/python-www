import functools
import time
import unittest

from . import dummy

import www

class CallmTestCase(unittest.TestCase):
    def setUp(self):
        return
        self.conn = dummy.Connection('www.dummy.com')
        self.conn = Connection()
        self.conn.host = 'www.dummy.com'

    def tearDown(self):
        self.conn = None

class TestResource(CallmTestCase):
    def test_basic(self):
        result = www.Resource('//example.com/foo/', kitten='fluffy')(mode='debug')
        expected = ('GET', '/foo/?kitten=fluffy', None, None)

class TestRequest(CallmTestCase):
    def test_basic(self):
        result = www.Request('//example.com/foo/', kitten='fluffy',
                mode='debug')()
        expected = ('GET', '/foo/?kitten=fluffy', None, {'User-Agent': www.USER_AGENT})

        self.assertEqual(result, expected)
