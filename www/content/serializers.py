import xml.dom.minidom as _xml
import json as _json

import www
from www.core import exceptions

def text(data):
    return str(data)

def form(data):
    return www.urlencode(data)

def xml(data):
    raise exceptions.NotAcceptable("NO XML")

def json(data, pretty=False, indent=4, sort_keys=True, json_p=None):
    if pretty:
        params = {'indent': indent, 'sort_keys': sort_keys}
    else:
        params = {}

    output = _json.dumps(data, **params)

    if json_p:
        output = '{}({});'.format(json_p, output)

    return output

def jpg(data):
    raise www.UnsupportedMediaType

def png(data):
    raise www.UnsupportedMediaType

def gif(data):
    raise www.UnsupportedMediaType

def pdf(data):
    raise www.UnsupportedMediaType

def zip(data):
    raise www.UnsupportedMediaType

def tar(data):
    raise www.UnsupportedMediaType

def mp3(data):
    raise www.UnsupportedMediaType

def mp4(data):
    raise www.UnsupportedMediaType

def avi(data):
    raise www.UnsupportedMediaType

def wav(data):
    raise www.UnsupportedMediaType

