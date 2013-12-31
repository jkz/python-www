import functools

class BindablePartial:
    """
    A partial method that is class bindable.
    """
    def __init__(self, *args, **kwargs):
        # To prevent any names from not being passable as kwargs
        # we assume the first `args` is the function

        self.method, *self.args = args
        self.kwargs = kwargs

        # Preserve method information
        for attr in functools.WRAPPER_ASSIGNMENTS:
            setattr(self, attr, getattr(self.method, attr))

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        partial = functools.partial(self.method, obj, *self.args, **self.kwargs)
        return functools.wraps(self.method)(partial)

    def __call__(self, *args, **kwargs):
        return functools.partial(self.method, *self.args, **self.kwargs)(*args, **kwargs)
