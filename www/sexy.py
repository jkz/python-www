from . import structures

class Query(structures.MultiDict):
    def __init__(self, *args, verbatim=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_verbatim = verbatim

    def verbatim(self):
        return '&'.join(('='.join(map(str, p)) for p in self.items(multi=True)))

    def encoded(self):
        return urlencode(self.items(multi=True))

    def __str__(self):
        if self.use_verbatim:
            return self.verbatim()
        else:
            return self.encoded()


class Header(structures.MultiDict):
    def __str__(self):
        return '\n'.join('{}: {}'.format(key, ','.join(map(str, vals))) for key, vals in self.listvalues())


class Request:
    class Error(Error): pass

    def __init__(
            self,
            url = '',
            method = 'GET',
            body = None,
            headers = None,
            resource = None,
            **kwargs
    ):
        self.resource = resource or Resource(url, **kwargs)

        self.method = method.upper()
        self.headers = Header(headers or {})
        self.body = body


    def __str__(self):
        return '{} {}'.format(self.method.upper(), self.resource)


class WSGIRequest(Request):
    def __init__(env):

    meta = {}
    headers = {}


    url = env.pop('PATH')
    query_string = env.pop('QUERY_STRING')

    for key in (
        'DOCUMENT_ROOT',
        #'HTTP_COOKIE',
        #'HTTP_HOST',
        #'HTTP_REFERER',
        #'HTTP_USER_AGENT',
        'HTTPS',
        #'PATH',
        #'QUERY_STRING',
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



class ClientRequest:
    def params(self):
        self.prepare()

        method = self.method.upper()

        url = self.resource.path

        if self.body is None and self.data and method in ('POST', 'PUT', 'PATCH'):
            body = Query(**self.data)
        else:
            body = self.body

        headers = self.headers.copy()
        return (method, url, body, headers)

    def stream(self, **kwargs):
        return self.resource.connection.start(self, **kwargs)

    def __call__(self):
        return self.resource.connection.fetch(*self.params())


class ServerRequest:

