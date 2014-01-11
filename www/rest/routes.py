from www.server.routes import *

from .endpoints import One, Few, All

def crud(path, resource, one=Int(), few=Ints(), **routes):
    "Set up all, few and one resource endpoints"
    return Route(path, All(resource),
            few = Route('/{uids}', Few(resource), uids=few),
            one = Route('/{uid}', One(resource), uid=one),
            **routes)

