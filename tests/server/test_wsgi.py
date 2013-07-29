import unittest


from www.server import wsgi
from www.server import responses

class TestWSGI(unittest.TestCase):
    def test_parse(self):
        env = wsgi.setup_environ()
        request = wsgi.parse(env)

        self.assertTrue('PATH_INFO' in request)
        self.assertEqual(request['PATH_INFO'], '/')

        self.assertEqual(request.headers['Content-Length'], None)
        self.assertEqual(request.headers['Content-Type'], None)
        self.assertEqual(request.headers['Host'], '127.0.0.1')

    def test_application(self):
        @wsgi.application
        def hello_world(request):
            return responses.Ok("Hello World!")

        env = wsgi.setup_environ()

        response = responses.Response()

        result = hello_world(env, response)

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(result, ['Hello World!'])

