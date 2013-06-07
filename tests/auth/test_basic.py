import unittest

import www
from www.auth import basic

class TestAuth(unittest.TestCase):
    def test_basic(self):
        # Taken from http://en.wikipedia.org/wiki/Basic_access_authentication
        token = basic.Token('Aladdin', 'open sesame')

        connection = www.Connection('//example.com')
        service = basic.Service(connection=connection, token=token)

        request = service.connection.create_request()
        request.prepare()

        result1 = request.headers['Authorization']

        request = basic.create_request('//example.com', username='Aladdin',
                password='open sesame')
        request.prepare()
        result2 = request.headers['Authorization']

        expected = 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='
        self.assertEqual(result1, expected)
        self.assertEqual(result2, expected)



