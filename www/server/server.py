import www

class Server:
    def request(self, *args, **kwargs):
        return www.Request(*args, **kwargs)

    def resolve(self, request):
        return www.Response(request)

    def application(self, *args, **kwargs):
        return self.resolve(self.request(*args, **kwargs))


