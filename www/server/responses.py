from www.core import exceptions
from www.core import http

class Response(http.Response, exceptions.Raisable):
    def write(self, data):
        #TODO: guarantee that the passed-in string was either completely sent
        # to the client, or that it is buffered for transmission while the
        # application proceeds onward.
        # http://www.python.org/dev/peps/pep-0333/#the-write-callable
        self.body.write(data)

    def __call__(self, status, headers):
        """
        Status is either of form
            "<code> <reason>"
        OR
            <code>

        Headers is a sequence of (key, value) pairs or a mapping.
        """
        #XXX: If a status is overwritten, but does not specify a reason, the
        #     old reason could persist, which might be unwanted behaviour
        if isinstance(status, str):
            code, reason = status.split(' ', 2)
            code = int(code)
        elif status:
            code = status

        self.headers.update(headers)

        return self.write

    #TODO dict interface
    '''
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
    '''

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

