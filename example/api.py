from www.rest import routes
from www.rest import stack
from www.server.routes import Route
from www.server.responses import Response
from www.server import wsgi

from . import dummy

class User(dummy.Dummy):
    pass

class Post(dummy.Dummy):
    pass

class UserPosts(dummy.Dummy):
    pass

api = Route('/api',
    users = routes.crud('/users', User()),
    posts = routes.crud('/posts', Post()),
)
api.users.one.routes['posts'] = Route('/posts', UserPosts())

wsgi.Server('localhost', 333, stack.build(api)).forever()

print(api.resolve('/api/users'))
print(api.resolve('/api/users/1'))
print(api.resolve('/api/users/1/posts'))
print(api.resolve('/api/users/1/posts/2'))


request = server.request(method='GET', url='/api/users')

request['method'] = 'POST'
request['data'] = {
    'name': 'Jesse the Game',
    'age': 24,
}
request['router'] = api

print(request)
try:
    print(str(server.resolve(request)))
except Response as response:
    print(str(response))

server = Server(routes=api)
request = server.request(method='GET', url='/api/users')
request['method'] = 'GET'
request['router'] = api
print(request)
print(server.resolve(request))


