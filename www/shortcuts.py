from www.client import client
from www.core import http

def url(*args, **kwargs):
    return http.Resource(*args, **kwargs).url

def absolute(*args, **kwargs):
    return http.Resource(*args, **kwargs).absolute

def query_string(*args, **kwargs):
    return str(http.Query(*args, **kwargs))

def request(url, **kwargs):
    return client.Request(url, **kwargs).fetch()

client.implement_methods(request, globals())
