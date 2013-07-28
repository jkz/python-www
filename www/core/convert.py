def query_string(query=(), verbatim=False, **kwargs):
    """
    A querystring builder class.

    Turns keyword arguments into a urlencoded querystring.

    query -- a dictionary or sequence of pair tuples
    verbatim -- turns off urlencoding when True
    """
    pairs = []
    try:
        pairs.extend(query.items())
    except AttributeError:
        pairs.extend(query)
    pairs.extend(kwargs.items())
    if verbatim:
        return '&'.join(('='.join(map(str, p)) for p in pairs))
    else:
        return urlencode(pairs)

def url(*args, **kwargs):
    return Resource(*args, **kwargs).url

def path(*args, **kwargs):
    return Resource(*args, **kwargs).path


