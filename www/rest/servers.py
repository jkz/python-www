from www.server import servers

class Server(servers.Server):
    def __init__(self, *args, routes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = routes

    def resolve(self, request):
        try:
            endpoint, request.kwargs = self.routes.resolve(request.resource.path)
        except TypeError:
            #This should handle 404s
            raise

        return endpoint(request)

