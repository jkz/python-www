import re
import collections

class Raisable(BaseException):
    pass

class Error(Raisable, Exception):
    pass

class Response(Raisable):
    version = 'HTTP/1.1'
    code = None
    payload = None
    headers = {}

    options = {}

    def __init__(self, request, code=None, payload=None, headers=None):
        self.request = request

        if code:
            self.code = code

        if payload is not None:
            self.payload = payload

        headers = self.headers.copy()
        self.headers = headers

        # Update dynamic headers
        for key, val in self.options.items():
            if callable(val):
                self[key] = val(request)
            elif isinstance(val, str):
                self[key] = val.format(**request)
            else:
                self[key] = val


        if headers:
            self.headers.update(headers)

        request

    def __str__(self):
        return '{} {}'.format(self.code, self.reason())

    def status(self):
        return ' '.join((self.version, self.code, self.reason))

    @property
    def reason(self):
        return ' '.join(s for s in re.split(r'([A-Z][a-z]*)', self.__class__.__name__) if s).upper()

    def __iter__(self):
        return self.headers.__iter__()

    def __getitem__(self, key):
        return self.headers[key]

    def __setitem__(self, key, val):
        self.headers[key] = val

    def __delitem__(self, key):
        del self.headers[key]

    def __len__(self):
        return len(self.headers)

    @property
    def update(self):
        return self.headers.update

class Response(Raisable):
    code = None
    payload = None
    headers = {}
    options = {}

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def complete(self, request, payload=None, headers={}):
        if payload is not None:
            self.payload = payload

        headers = self.headers.copy()
        self.headers = headers

        # Update dynamic headers
        for key, val in self.options.items():
            if callable(val):
                self[key] = val(request)
            elif isinstance(val, str):
                self[key] = val.format(**request)
            else:
                self[key] = val

        if headers:
            self.headers.update(headers)


class Templated:
    template = ''

    @property
    def payload(self):
        return template.format(**self.request)

class Information(Response):
    "code = 1xx"


class Success(Response):
    "code = 2xx"

class Ok(Success):
    code = 200

class Created(Success):
    code = 201

    options = {
        'Location': lambda r: r['location'],
    }

class Accepted(Success):
    code = 202

    options = {
        'Location': lambda r: r['location'],
        # 'Retry-After': estimated time of completion
    }

class NoContent(Success):
    code = 204




class Redirect(Response):
    "code = 3xx"

    options = {
        'Location': lambda r: r['location'],
    }

class MovedPermanently(Redirect):
    code = 301

class Found(Redirect):
    code = 302

class SeeOther(Redirect):
    code = 303

class NotModified(Redirect):
    code = 304

class UseProxy(Redirect):
    code = 305

class TemporaryRedirect(Redirect, Templated):
    code = 307

    payload = 'Temporarily redirected to <a href="{location}">{location}</a>'




class ClientError(Response):
    "code = 4xx"

class BadRequest(ClientError):
    code = 400

class Unauthorized(ClientError):
    code = 401

class Forbidden(ClientError):
    code = 403

class NotFound(ClientError):
    code = 404
    payload = "Resource could not be located."

class MethodNotAllowed(ClientError):
    code = 405
    payload = "Method is not allowed on this resource."

class NotAcceptable(ClientError):
    code = 406
    payload = "Can not provide acceptable response."

class Conflict(ClientError):
    code = 409
    payload = "Could not complete because of conflicting arguments."

class UnsupportedMediaType(ClientError):
    code = 415
    payload = "Data format provided was invalid."

class UnprocessableEntity(ClientError):
    code = 422
    payload = "Data does not represent a valid entity."

class TooManyRequests(ClientError):
    code = 429
    payload = "Too many requests, please slow down."


class ServerError(Response):
    "code = 5xx"

class InternalServerError(ServerError):
    code = 500

class NotImplemented(ServerError):
    code = 501

class BadGateway(ServerError):
    code = 502

class ServiceUnavailable(ServerError):
    code = 503

class GatewayTimeout(ServerError):
    code = 504

class HttpVersionNotSupported(ServerError):
    code = 505

