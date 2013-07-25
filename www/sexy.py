import www
import io

from . import structures

class Method:
    def convert(self, verb):
        if verb is not None:
            VERB = verb.upper()
            if not self.allow_custom and VERB not in www.methods.ALL:
                raise www.MethodNotAllowed(VERB)
        return verb

    def __init__(self, verb=None, allow_custom=False):
        self.verb = self.convert(verb)
        self.allow_custom = allow_custom

    def __set__(self, instance, verb):
        self.verb = self.convert(verb)

    def __get__(self, instance, owner):
        return self.verb


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


class Body:
    """
    An interface to all kinds of request bodies.
    """
    def __init__(self, body):
        self.body = body

    def read(self, size):
        return self.body.read()

    def readline(self):
        return self.body.readline()

    def readlines(self, hint):
        return self.body.readlines(hint)

    def __iter__(self):
        return self.body.__iter__()

    def __str__(self):
        return str(self.body)


class ErrorStream:
    def flush(self):
        pass

    def write(self, str):
        pass

    def writelines(self, seq):
        pass


class Request:
    class Error(Error): pass

    def __init__(
            self,
            url = '',
            method = None,
            body = None,
            headers = None,
            meta = None,
            resource = None,
            **kwargs
    ):
        # (. )( .)! Not all named arguments are passed to the Resource.
        self.resource = resource or Resource(url, **kwargs)
        self.method = Method(method)
        self.headers = Header(headers or {})
        self.body = Body(body or io.StringIO())
        self.meta = Meta(meta or {})

    def __str__(self):
        return '{} {}'.format(self.method, self.resource)


class Response:
    def __init__(self,
            status,
            reason=None,
            headers=None,
            body=body,
    ):
        self.status = status
        self.reason = reason
        self.headers = Header(headers or {})
        self.body = Body(body or io.StringIO())
