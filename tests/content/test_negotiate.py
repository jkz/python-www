import unittest

from www.content import negotiate

class TestNegotiate(unittest.TestCase):
    def test_basic(self):
        allowed = 'json', 'xml', 'form', 'text'

        self.assertEqual(negotiate.value(allowed, 'application/json'),
        'json')
        self.assertEqual(negotiate.value(allowed, 'xml'), 'xml')
        self.assertEqual(negotiate.value(allowed, 'none'), None)

        header = ','.join(('application/xbel+xml', 'text/xml', 'text/*;q=0.5','*/*; q=0.1'))
        self.assertEqual(negotiate.range(allowed, header), 'xml')

        self.assertEqual(negotiate.range(['json'], header), 'json')
