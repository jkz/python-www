from www.utils.decorators import lazy_property

from . import responses

class Layer:
    def __init__(self, application):
        self.application = application

    def __call__(self, request):
        return self.resolve(request)

class Endpoint:
    def resolve(self, request):
        return responses.OK()

    def __call__(self, request):
        return self.resolve(request)


class Stack(list):
    """
    Take any amount of middleware and return it as a single one.
    """
    def insert(self, index, value, after=True):
        # Insert a layer after the item at index
        if isinstance(index, int):
            # Update index to insert behind given index rather than before
            if after:
                index += 1
            return super().insert(index, value)

        # Find a class with given name and user it as the index
        elif isinstance(index, str):
            for i, e in enumerate(list):
                if getattr(e, '__name__', e.__class__.__name__) == str:
                    return self.insert(i, value, after)

        # Find the index of given object on the stack and insert the layer
        # If the object is not present, a value error is raised
        self.insert(self.index(index), value, after)

    def __add__(self, other):
        """
        Append the other stack (or list of layers)
        """
        combined = super().__add__(other)
        return self.__class__(combined)

    def __call__(self, app):
        """
        Decorate given app by the full stack of layers.
        """
        for wrap in reversed(self):
            app = wrap(app)
        return app


class Cache(Layer):
    """
    Checks if valid data is available in a (temporary) storage backend.
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
        response = self.application(request)

        # Cache the fresh response if the request is cachable
        if self.cachable(request):
            self.set(self.key(request), response)

        return response


class Guard(Layer):
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
            return self.application(request)


class Option(Layer):
    """
    Enriches the request object.
    """
    def resolve(self, request):
        pass

    def __call__(self, request):
        print('OPTION', self)
        self.resolve(request)
        return self.application(request)

