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

