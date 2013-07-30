class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, request):
        return self.app(request)


class Stack:
    """
    Take any amount of middleware and return it as a single one.
    """
    def __init__(self, *apps):
        self.apps = apps

    def __call__(self, app):
        for wrap in reversed(self.apps):
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
        if self.cachable(request)
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
            raise self.resolve(request):
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

