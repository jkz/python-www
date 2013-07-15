import www
import xml.dom.minidom as _xml
import json as _json

def form(raw):
    return dict(www.parse_qsl(raw))

def json(raw):
    return _json.loads(raw)

def text(raw):
    return raw

def xml(raw):
    return _xml.parseString(raw)

