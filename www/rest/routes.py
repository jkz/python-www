from www import content
from www.server import routes

from . import endpoints
from . import views

class Format(routes.Str):

    """
    A route part that matches content types
    """
    pattern = '|'.join(content.TYPES)
    optional = True

class Route(routes.Route):
    """A special route which always adds a format extension child"""
    def __init__(self, pattern, endpoint=None, **kwargs):
        super().__init__(pattern, endpoint, **kwargs)
        if endpoint:
            self.routes['format'] = routes.Route(r'\.{format}', endpoint, format=Format())

def crud(path, resource, one=routes.Int(), few=routes.Ints(), **subroutes):
    "Set up all, few and one resource endpoints"
    return Route(path, endpoints.All(resource),
        #new = Route('/new', views.New(resource)),
        #schema = Route('/schema', views.Schema(resource)),

        few = Route('/{uids}', endpoints.Few(resource), uids=routes.Int()),
        one = Route('/{uid}', endpoints.One(resource), uid=routes.Ints(),
            #edit = Route('/edit', views.Edit(resource))
        ),
        **subroutes)
