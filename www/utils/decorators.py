import functools

def default_kwargs(**defaults):
    def wrap(func):
        @functools.wraps(func)
        def funk(*args, **kwargs):
            # Copy the defaults so they don't get messed up in place
            _kwargs = defaults.copy()
            _kwargs.update(kwargs)
            return func(*args, **_kwargs)
        return funk
    return wrap

def cached_property(f):
    """returns a cached property that is calculated by function f"""
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x

    return property(get)


class lazy_property:
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent static data, as it can not be reevaluated.
    """
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value
