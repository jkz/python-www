import www
import mimeparse
import xml.dom.minidom as _xml
import json as _json

from www.utils import cached_property

from . import options as o
from . import fields as f
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

def accept_header(allowed, header):
    match = mimeparse.best_match(mime_list(allowed), header)
    type = TYPES.get(match)
    if type not in allowed:
        raise exceptions.NotAcceptable(header)
    return type

def content_type_header(allowed, header):
    #see http://www.ietf.org/rfc/rfc2616.txt section 7.2.1
    #type = TYPES.get(header, 'application/octet-stream')
    type = TYPES.get(header)
    if type not in allowed:
        raise exceptions.UnsupportedMediaType(header)
    return type

class Negotiator(Option):
    options = {}

    def __init__(self, choices=(), options=None, **kwargs):
        if not choices:
            #XXX Conf error or such
            raise Exception("Allowed accept types can't be empty")

        kwargs['options'] = kwargs.pop('options', dict(
            as_kwarg  = 'ext',
            as_query  = 'format',
        ))

        as_header = ('Accept', self.parse_header),

        kwargs['field'] = kwargs.pop('field', f.String())

        super().__init__(**kwargs)

        if not self.field.choices:
            self.field.choices = choices

        if not self.field.default:
            self.field.default = self.field.choices[0]

class Accept(Negotiator):
    options = {
        as_kwarg  = 'ext',
        as_query  = 'format',
    }

    def parse_header(self, header):
        return accept_header(self.field.choices, header)


class ContentType(Negotiator):
    options = {
        as_query  = 'content_type',
    }

    def parse_header(self, header):
        return content_type(self.field.choices, header)


class Language(Negotiator):
    options = {
        as_kwarg  = 'lang',
        as_query  = 'lang',
    }


class Accept(Option):
    def parse_header(self, header):
        return accept_header(self.field.choices, header)

    def __init__(self, choices=(), **kwargs):
        if not choices:
            #XXX Conf error or such
            raise Exception("Allowed accept types can't be empty")

        kwargs['options'] = kwargs.pop('options', dict(
            as_kwarg  = 'ext',
            as_query  = 'format',
            as_header = ('Accept', self.parse_header),
        ))

        kwargs['field'] = kwargs.pop('field', f.String())

        super().__init__(**kwargs)

        if not self.field.choices:
            self.field.choices = choices

        if not self.field.default:
            self.field.default = self.field.choices[0]

        if not self.field.help_text:
            self.field.help_text = "The response data format"


class ContentType(Option):
    def parse_header(self, header):
        return content_type(self.field.choices, header)

    def __init__(self, choices=(), **kwargs):
        if not choices:
            #XXX Conf error or such
            raise Exception("Allowed content types can't be empty")

        kwargs['options'] = kwargs.pop('options', dict(
            as_query  = 'content_type',
            as_header = ('Content-Type', self.parse_header),
        ))

        kwargs['field'] = kwargs.pop('field', f.String())

        super().__init__(**kwargs)

        if not self.field.choices:
            self.field.choices = choices

        if not self.field.default:
            self.field.default = self.field.choices[0]

        if not self.field.help_text:
            self.field.help_text = "The request data format",


class Language(Option):
    def __init__(self, choices=(), **kwargs):
        if not choices:
            #XXX Conf error or such
            raise Exception("Allowed languages can't be empty")

        kwargs['options'] = kwargs.pop('options', dict(
            as_kwarg  = 'lang',
            as_query  = 'lang',
            as_header = 'Accept-Language',
        ))

        kwargs['field'] = kwargs.pop('field', f.String())

        super().__init__(**kwargs)

        if not self.field.choices:
            self.field.choices = choices

        if not self.field.default:
            self.field.default = self.field.choices[0]

        if not self.field.help_text:
            self.field.help_text = "The repsonse data language"


class Negotiate(layers.Layer):
    """
    The Negotiate layer parses accept and content types from the request
    and stores them in the request options.
    """
    # The options are ordered by preference (making the first default)
    accept_types = 'json', 'text'
    content_types = 'json', 'form', 'text'
    languages = 'en', 'nl'

    @cached_property
    def options(self):
        return o.Options(
            accept_type = Accept(self.accept_types),
            content_type = ContentType(self.content_types),
            language = Language(self.languages),
        )

def negotiate(
    accept = ('json', 'text'),
    content = ('json', 'form', 'text'),
    languages = ('en', 'nl'),
):
    """
    The Negotiate layer parses accept and content types from the request
    and stores them in the request options.
    """
    # The options are ordered by preference (making the first default)
    return o.Options(
        accept_type = Accept(accept),
        content_type = ContentType(content),
        language = Language(languages),
    )


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
        return _xml.parseString(body)


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
        pretty = o.Option(
            as_query  = 'pretty',
            field = f.Boolean(
                default   = False,
                help_text = "When 'true' the json is formatted nicely.",
            )
        ),
        indent = o.Option(
            as_query  = 'indent',
            field = f.Integer(
                default   = 4,
                help_text = "Number of indentation spaces for pretty json.",
            )
        ),
        sort_keys = o.Option(
            as_query  = 'sort_keys',
            field = f.Boolean(
                default   = True,
                help_text = "When 'true' the keys are sorted"
            )
        ),
    )
    def json(self, request, data):
        params = {}
        if request['pretty']:
            params['indent'] = request['indent']
            params['sort_keys'] = request['sort_keys']
        return _json.dumps(data, **params)

    @layers.options(
        json_p = o.Option(
            as_query  = 'callback',
            field = f.String(
                help_text = "The local callback function that wraps the
                response",
            )
        ),
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

