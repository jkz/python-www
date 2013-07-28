from www import client
from www import core

def url(*args, **kwargs):
    return core.Resource(*args, **kwargs).url

def path(*args, **kwargs):
    return core.Resource(*args, **kwargs).path

def query_string(*args, **kwargs):
    return str(core.Query(*args, **kwargs))

def request(url, **kwargs):
    return client.Request(url, **kwargs).fetch()

implement_methods(request, globals())
