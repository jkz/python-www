import unittest

from www import shortcuts

class TestShortcuts(unittest.TestCase):
    def test_url(self):
        self.assertEqual(shortcuts.url('example.com'), 'http://example.com')
        self.assertEqual(shortcuts.url('example.com', key='val'), 'http://example.com?key=val')
        self.assertEqual(shortcuts.url('example.com', scheme='https'), 'https://example.com')
        self.assertEqual(shortcuts.url('example.com', fragment='fragment'), 'http://example.com#fragment')

    def test_get(self):
        # This is not a real test
        response = shortcuts.get('http://localhost')
        self.assertEqual(response.code, 200)

