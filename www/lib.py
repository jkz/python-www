# This module combines urllib/urlparse into one universal api
try:
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit, quote
except ImportError:
    from urllib import urlencode, quote
    from urlparse import parse_qsl, urlsplit, urlunsplit

