import www
import mimeparse

import json as _json

from . import exceptions
from . import layers

# Maps all convertor names to mime types
TYPES = {
    'text': 'text/plain',
    'json': 'application/json',
    'jsonp': 'application/javascript',
    'form': 'application/x-www-form-urlencoded',
    'xml': 'application/xml',
    'mp3': 'audio/mpeg',
    'bytes': 'application/octet-stream',
}

# Maps all mime types to convertor names
MIMES = {
    'text/plain': 'text',
    'application/json': 'json',
    'application/x-www-form-urlencoded': 'form',
    'application/xml': 'xml',
    'audio/mpeg': 'mp3',
    'application/octet-stream': 'bytes',
}

def mime_list(types):
    """
    Return a list of convertors prepared for mimeparse.best_match
    """
    for type in reversed(types):
        yield MIMES.get(type, type)

class Negotiate(layers.Layer):
    """
    The Negotiate layer parses accept and content types from the request
    and stores them in the request options.
    """
    # The options are ordered by preference (making the first default)
    accept_types = 'json', 'text'
    content_types = 'json', 'form', 'text'
    languages = 'en', 'nl'

    @property
    def options(self):
        return {
            'accept_type': [
                ('kwargs', 'ext'),
                ('query', 'format'),
                ('headers', 'Accept', self.accept_header),
                self.accept_types[0]
            ],
            'content_type': [
                ('query', 'content_type'),
                ('headers', 'Content-Type', self.content_type_header),
                self.content_types[0]
            ],
        }

    def accept_header(self, header):
        match = mimeparse.best_match(mime_list(self.accept_types), header)
        type = TYPES.get(match)
        if type not in self.accept_types:
            raise exceptions.NotAcceptable(header)
        return type

    def content_type_header(self, header):
        #see http://www.ietf.org/rfc/rfc2616.txt section 7.2.1
        #type = TYPES.get(header, 'application/octet-stream')
        type = TYPES.get(match)
        if type not in self.accept_types:
            raise exceptions.UnsupportedMediaType(header)
        return type


class Deserialize(layers.Layer):
    def call(self, request):
        if request.body:
            content_type = parse_type(request['content_type'])
            return getattr(self, content_type)(request.body)

    def form(self, body):
        return dict(www.parse_qsl(body))

    def json(self, body):
        return _json.loads(body)

    def text(self, body):
        return body

    def xml(self, body):
        raise exceptions.UnsupportedMediaType("NO XML")



class Serialize(layers.Layer):
    def call(self, request, data):
        accept_type = parse_type(request['accept_type'])
        return getattr(self, accept_type)(request, data)

    def text(self, request, data):
        return str(data)

    def form(self, request, data):
        return www.urlencode(data)

    def xml(self, request, data):
        raise exceptions.NotAcceptable("NO XML")

    @layers.options(
        pretty = [
            ('query', 'pretty', lambda x: x == 'true'),
            False
        ],
        indent = [
            ('query', 'indent', int),
            4
        ],
        sort_keys = [
            ('query', 'sort_keys', lambda x: x == 'true'),
            True
        ],
    )
    def json(self, request, data):
        params = {}
        if request['pretty']:
            params['indent'] = request['indent']
            params['sort_keys'] = request['sort_keys']
        return _json.dumps(data, **params)

    @layers.options(
        jsonp = [
            ('query', 'callback'),
        ]
    )
    def jsonp(self, request, data):
        if not request['jsonp']:
            raise exceptions.NotAcceptable({'callback':
                "No jsonp callback specified"})
        return '{}({});'.format(request['jsonp'], self.json(data))

    def jpg(self, request, data):
        raise www.UnsupportedMediaType

    def png(self, request, data):
        raise www.UnsupportedMediaType

    def gif(self, request, data):
        raise www.UnsupportedMediaType

    def pdf(self, request, data):
        raise www.UnsupportedMediaType

    def zip(self, request, data):
        raise www.UnsupportedMediaType

    def tar(self, request, data):
        raise www.UnsupportedMediaType

    def mp3(self, request, data):
        raise www.UnsupportedMediaType

    def mp4(self, request, data):
        raise www.UnsupportedMediaType

    def avi(self, request, data):
        raise www.UnsupportedMediaType

    def wav(self, request, data):
        raise www.UnsupportedMediaType

