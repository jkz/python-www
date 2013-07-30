import www
import mimeparse
import xml.dom.minidom as _xml
import json as _json

from www.utils import cached_property

from . import options as o
from . import fields as f
from . import exceptions
from . import layers

class Negotiator(Option):
    help_text = "This is a negotiator"

    def __init__(self, *choices, options=None, **kwargs):
        # Negotiator always needs a range of options. (Otherwise there would be
        # nothing to negotiate.
        if not choices:
            #XXX Conf error or such
            raise Exception("Choices can't be empty")

        # The negotiatior provides a default string field when it's not given
        kwargs['field'] = kwargs.pop('field', f.String())

        super().__init__(**kwargs)

        # Ensure choices and default for the field
        if not self.field.choices:
            self.field.choices = choices

        if not self.field.default:
            self.field.default = self.field.choices[0]

        if not self.field.help_text:
            self.field.help_text = self.help_text


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
            accept_type = Accept(*self.accept_types),
            content_type = ContentType(*self.content_types),
            language = Language(*self.languages),
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
        accept_type = Accept(*accept),
        content_type = ContentType(*content),
        language = Language(*languages),
    )


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

@layers.options(
    json_p = o.Option(
        as_query  = 'callback',
        field = f.String(
            help_text = "The local callback function that wraps the
            response",
        )
    ),
)
