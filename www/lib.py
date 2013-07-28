# This module combines urllib/urlparse into one universal api
try:
    from urllib.parse import parse_qsl, urlencode, urlsplit as _urlsplit, urlunsplit, quote
except ImportError:
    from urllib import urlencode, quote
    from urlparse import parse_qsl, urlsplit as _urlsplit, urlunsplit

def urlsplit(url, auto_prefix=False):
    if (auto_prefix
    and not url.startswith('http://')
    and not url.startswith('https://')
    and not url.startswith('/')):
        url = '//' + url
    return _urlsplit(url)
