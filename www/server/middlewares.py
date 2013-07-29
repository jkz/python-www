from www.core import content
from .middleware import Middleware

class Router(Middleware):
    #TODO set router

    def resolve(self, request):
        try:
            endpoint, kwargs = self.router.resolve(request.path)
        #404
        except TypeError:
            response(404)
            return []

        request['endpoint'] = endpoint
        request['kwargs'] = kwargs

        return self.application(request)


class Accept(Negotiator):
    as_kwarg  = 'ext'
    as_query  = 'format'

    help_text = "The response data format"

    @property
    def as_header(self):
        return ('Accept', lambda: self, header:
                accept_header(self.field.choices, header))


class ContentType(Negotiator):
    as_query  = 'content_type'

    help_text = "The request data format"

    @property
    def as_header(self):
        return ('Content-Type', lambda: self, header:
                content_type(self.field.choices, header))


class Language(Negotiator):
    as_kwarg  = 'lang'
    as_query  = 'lang'
    as_header = 'Accept-Language'

    help_text = "The response data language"


class Deserialize(Middleware):
    def resolve(self, request, response):
        request['data'] = content.deserialize(request.body,
                request['Content-Type'])
        return self.application(request, response)


class Serialize(Middleware):
    def resolve(self, request, response):
        data = self.application(request, response)
        serialized = content.serialize(data, response['content-type'])
        response['Content-Length'] = len(serialized)
        return serialized

