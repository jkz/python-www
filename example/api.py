from www.rest.routes import crud
from www.server.routes import Route
from www.server.responses import Response
from www.server.middlewares import server as _server_

from . import dummy

class User(dummy.Dummy):
    pass

class Post(dummy.Dummy):
    pass

class UserPosts(dummy.Dummy):
    pass

api = Route('/api',
    users = crud('/users', User()),
    posts = crud('/posts', Post()),
)
api.users.one.routes['posts'] = Route('/posts', UserPosts())

print(api.resolve('/api/users'))
print(api.resolve('/api/users/1'))
print(api.resolve('/api/users/1/posts'))
print(api.resolve('/api/users/1/posts/2'))

Stack

server = _server_('localhost', 333, api)
server.forever()

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


