from www.client import client
from . import http, stack

class Server(stack.Server):
    def request(self, *args, **kwargs):
        return self.resolve(http.Request(*args, **kwargs))

client.implement_methods(Server.request, Server, True)

def server(host, port, *args, **kwargs):
    return Server(host, port, stack.build(*args, **kwargs))

