import unittest

from www import shortcuts

class TestShortcuts(unittest.TestCase):
    def test_url(self):
        self.assertEqual(shortcuts.url('google.com'), 'http://google.com')
        self.assertEqual(shortcuts.url('google.com', foo='bar'), 'http://google.com?foo=bar')
        self.assertEqual(shortcuts.url('google.com', scheme='https'), 'https://google.com')
        self.assertEqual(shortcuts.url('google.com', fragment='fragment'), 'http://google.com#fragment')

    def test_get(self):
        # This is not a real test
        response = shortcuts.get('http://localhost')
        self.assertEqual(response.code, 200)

