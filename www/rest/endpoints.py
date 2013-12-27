from www.server import endpoints, responses

class Endpoint(endpoints.Endpoint):
    def envelope(self, status, meta):
        return lambda body: {'code': status, 'meta': meta, 'data': body}

    @property
    def schemas(self):
        return self.resource.schemas

    #XXX Somehow this should find all available options and add them to the
    #    response. The adding of the options metadata could be responsibility
    #    of the options.Option class, this method would then only need to
    #    add them to the response body
    def OPTIONS(self, request):
        "Return the endpoints and subresources of this resource"
        meta = {}
        meta['name'] = self.resource.name
        meta['links'] = request['router'].endpoints[self].meta()
        meta['methods'] = {}
        #XXX Perhaps there should be a meta decorator that provides the
        #    information
        for method in self.methods:
            meta['methods'][method] = getattr(self, method).__doc__
        return meta

class One(Endpoint):
    methods = {'GET', 'DELETE', 'PUT', 'PATCH', 'OPTIONS'}

    def identify(self, request):
        return request['kwargs']['uid']

    @property
    def schemas(self):
        return self.resource.schemas['entity']

    @property
    def name(self):
        return self.resource.name + '.one'

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
    methods = {'GET', 'DELETE', 'PUT', 'PATCH', 'OPTIONS'}

    def identify(self, request):
        return request['kwargs']['uids']

    @property
    def schemas(self):
        return self.resource.schemas['entity']

    @property
    def name(self):
        return self.resource.name + '.few'

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
    methods = {'GET', 'POST', 'DELETE', 'PATCH', 'OPTIONS'}

    @property
    def schemas(self):
        return self.resource.schemas['collection']

    @property
    def name(self):
        return self.resource.name

    def POST(self, request):
        "Append a new entity or collection"
        uid = self.resource.create(request['data'])
        location = self.reverse(request, uid=uid)
        raise responses.Created(location=location)

    def GET(self, request):
        "Return a filtered collection"
        objects = self.resource.query(request)
        return self.resource.slice(objects)

    def PATCH(self, request):
        "Update each element of a filtered collection with the same patch"
        objects = self.resource.query(request)
        self.resource.batch(request, objects)

    def DELETE(self, request):
        "Delete a filtered collection"
        self.resource.drop(request)
