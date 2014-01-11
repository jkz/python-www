from www.server import middleware
from www.server import routes
from www.content import TYPES

from . import views

class Format(routes.Str):
    pattern = '|'.join(TYPES)
    optional = True

class Route(routes.Route):
    """This route adds a format extension"""
    def __init__(self, pattern, endpoint=None, **kwargs):
        super().__init__(pattern, endpoint, **kwargs)
        self.routes['format'] = routes.Route(r'\.{format}', endpoint, format=Format())

class Api(middleware.Layer):
    """
    This is a helper class to provide convenient ways to glue
    an api together.
    """

    def __init__(self, routes=None, stack=None):
        self.routes = route or routes.Route('')
        self.stack = stack or middleware.Stack()

    def route(self, endpoint):
        def func(resource):

        pass

    def crud(self, resource, **routes):
        "Set up all, few and one resource endpoints"
        return Route(path, All(resource),
                new = Route('/new', views.New(resource)),
                schema = Route('/schema', views.Schema(resource)),

                few = Route('/{uids}', Few(resource), uids=Int()),
                one = Route('/{uid}', One(resource), uid=Ints(),
                    edit = Route('/edit', views.Edit(resource)))),
                **routes)

    def resolve(self, request):
        try:
            endpoint, kwargs = self.router.resolve(request.path)
        #404
        except TypeError:
            raise responses.NotFound()

        request['endpoint'] = endpoint
        request['kwargs'] = kwargs

        return self.stack(endpoint)(request)

