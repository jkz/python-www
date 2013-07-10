from www.server.routes import Route
from www.server.endpoints import Endpoint

class One(Endpoint):
    methods = {'GET', 'DELETE', 'PUT', 'PATCH'}

    options = dict(
        identifier = o.Option(
            as_kwarg = 'uid',
            help_text = "A unique identifier without a slash",
        ),
    )

    def GET(self, request):
        "Return an identified entity"
        return self.resource.fetch(request['identifier'])

    def PATCH(self, request):
        "Update an identified entity"
        return self.resource.update(request['identifier'], request['data'])

    def DELETE(self, request):
        "Delete an identified entity"
        self.resource.delete(request['identifier'])

    def PUT(self, request):
        "Replace or create an entity"
        return self.resource.replace(request['identifier'], request['data'])


class Few(Endpoint):
    methods = {'GET', 'DELETE', 'PUT', 'PATCH'}

    options = dict(
        identifier = o.Option(
            as_kwarg = 'uids',
            help_text = "A list of identifiers without a slash",
        ),
    )

    def GET(self, request):
        "Return the identified collection"
        return tuple(self.resource.fetch(i) for i in request['identifier'])

    def DELETE(self, request):
        "Delete an identified collection"
        for i in request['identifier']:
            self.resource.delete(i)

    def PUT(self, request):
        "Replace or create a collection"
        raise responses.NotImplemented

    def PATCH(self, request):
        "Update an identified collection"
        raise responses.NotImplemented


class All(Endpoint):
    methods = {'GET', 'POST', 'DELETE', 'PATCH'}

    def POST(self, request):
        "Append a new entity or collection"
        uid = self.resource.create(request['data'])
        #TODO put the reverse/location function in the proper place
        raise responses.Created(request, location=self.reverse(uid=uid))

    def GET(self, request):
        "Return a filtered collection"
        objects = self.resource.query(request)
        return self.resource.slice(objects)

    def PATCH(self, request):
        "Update each element a filtered collection with the same patch"
        objects = self.resource.query(request)
        self.resource.bulk_update(request, objects)

    def DELETE(self, request):
        "Delete a filtered collection"
        self.resource.bulk_delete(request)


def crud_route(resource, one=Int(), few=Ints()):
    "Set up all, few and one resource endpoints"
    return Route('/' + resource.name, All(resource),
            few = Route('/{uids}', Few(resource), uids=few),
            one = Route('/{uid}', One(resource), uid=one),
