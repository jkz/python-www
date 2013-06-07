import unittest

import www
from www.auth import oauth2

class TestAuth(unittest.TestCase):
    def test_signature_tumblr(self):
        creds = dict(
            client_id = 'CLIENT_ID',
            client_secret = 'CLIENT_SECRET')
        request = oauth2.create_request('http://example.com', **creds)
        request.prepare()

        computed = request.resource.url
        expected = 'http://example.com?client_id=CLIENT_ID'
        self.assertEqual(computed, expected)

        creds['access_token'] = 'ACCESS_TOKEN'
        request = oauth2.create_request('//example.com', **creds)
        request.prepare()

        computed = request.resource.url
        expected = 'http://example.com?access_token=ACCESS_TOKEN'
        self.assertEqual(computed, expected)
