import www

class Server:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port

    def request(self, *args, **kwargs):
        return www.Request(*args, **kwargs)

    def resolve(self, request):
        response = www.Response(request)
        return ('{} {}'.format(response.code, response.reason)
                str(response.header)
                response.body


    def application(self, *args, **kwargs):
       status, headers, body = self.resolve(self.request(*args, **kwargs))
       status = '200 OK'
       response_headers = [('Content-Type', 'text/plain'),
                      ('Content-Length', str(len(response_body)))]
       start_response(status, response_headers)

       return [response_body]



import wsgiref

class WSGIServer:
    def parse_cgi_environment(self, env):

        meta = {}
        headers = {}

        for key in (
            'DOCUMENT_ROOT',
            #'HTTP_COOKIE',
            #'HTTP_HOST',
            #'HTTP_REFERER',
            #'HTTP_USER_AGENT',
            'HTTPS',
            'PATH',
            'QUERY_STRING',
            'REMOTE_ADDR',
            'REMOTE_HOST',
            'REMOTE_PORT',
            'REMOTE_USER',
            'REQUEST_METHOD',
            'REQUEST_URI',
            'SCRIPT_FILENAME',
            'SCRIPT_NAME',
            'SERVER_ADMIN',
            'SERVER_NAME',
            'SERVER_PORT',
            'SERVER_SOFTWARE',
        ):
            meta[key] = env.pop(key)

        for key, val in env.items():
            # Remove 'HTTP_' from keys, then lower and replace '_' by '-'
            headers[key[5:].lower().replace('_', '-')] = val

        return meta, headers

    def application(self, environ, start_response):
        request = self.request(environ)
        status, headers, body = self.resolve(self.request(*args, **kwargs))
        status = '200 OK'
        response_headers = [('Content-Type', 'text/plain'),
                      ('Content-Length', str(len(response_body)))]
        start_response(status, response_headers)

        return [response_body]

    def serve(self, forever=True):
        httpd = wsgiref.make_server(self.host, self.port, self.application)
        if forever:
            httpd.serve_forever()
        else:
            http.handle_request()

