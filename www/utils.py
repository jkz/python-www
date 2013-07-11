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
