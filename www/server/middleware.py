from www.utils.decorators import lazy_property

class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, request):
        return self.app(request)


class Stack(list):
    """
    Take any amount of middleware and return it as a single one.
    """
    def insert(self, index, value):
        if isinstance(index, int):
            return super().insert(index, value)
        elif isinstance(index, str):
            for i, e in enumerate(list):
                if getattr(e, '__name__', e.__class__.__name__) == str:
                    return self.insert(i, value)
        self.insert(self.index(index), value)

    def __call__(self, app):
        for wrap in reversed(self):
            app = wrap(app)
        return app


class Cache(Middleware):
    """
    Checks if valid data is available in a temporary storage backend.
    This should wrap an application and its resolve method should return
    a response in a format that is expected from the wrapped application.
    """
    def key(self, request):
        return request.split()

    def get(self, key):
        pass

    def set(self, key, val):
        pass

    def delete(self, key):
        pass

    def cachable(self, request):
        return False

    def __call__(self, request):
        # If cache has a valid entry, return it
        cached = self.get(self.key(request))
        if cached:
            return cached

        # Get a fresh response
        response = self.app(request)

        # Cache the fresh response if the request is cachable
        if self.cachable(request):
            self.set(self.key(request), response)

        return response


class Guard(Middleware):
    """
    Raises responses (to bypass non-exceptionhandled middlewares)
    if a request does not pass the guard. Else returns the application's
    response.
    """
    def resolve(self, request):
        pass

    def __call__(self, request):
        try:
            raise self.resolve(request)
        except TypeError:
            return self.app(request)


class Option(Middleware):
    """
    Enriches the request object.
    """
    def resolve(self, request):
        pass

    def __call__(self, request):
        self.resolve(request)
        return self.app(request)

