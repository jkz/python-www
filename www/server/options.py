class RequestOption(Option):
    #XXX This is ugly :( OrderedDict?
    order = (
        'as_query',
        'as_kwarg',
        'as_header',
        'as_meta',
        'as_lambda',
        'as_method',
    )
    containers = {
        'as_query':  lambda self, obj, val: obj.query[val],
        'as_kwarg':  lambda self, obj, val: obj.kwargs[val],
        'as_header': lambda self, obj, val: obj.headers[val],
        'as_meta':   lambda self, obj, val: obj.meta[val],
        'as_lambda': lambda self, obj, val: val(obj),
        'as_method': lambda self, obj, val: getattr(self, val)(obj)
    }

def get_ip(request):
    """Extract the caller's IP"""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.meta.get('REMOTE_ADDR')
    return ip

