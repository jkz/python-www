from www.rest import routes
from www.rest import stack
from www.server.http import Request
from www.server.routes import Route, Str
from www.server.responses import Response
from www.server import wsgi
from www.server import test

from . import dummy
from . import fs

class User(dummy.Dummy):
    pass

class Post(dummy.Dummy):
    pass

class UserPosts(dummy.Dummy):
    pass

class File(fs.Resource):
	root = '/tmp/resttestdata'

api = Route('/api',
	dummy = Route('/dummy',
	    users = routes.crud('/users', User()),
	    posts = routes.crud('/posts', Post()),
    ),
	files = Route('/fs/{path}', fs.Endpoint(File()), path=Str('.*'))
)
print('api.files')
print(api.files)
print(api.files.pattern)
print(api.dummy.users)
print(api.dummy.users.pattern)
print(api.dummy.users.one)
print(api.dummy.users.one.pattern)
print(api.files._parts)
api.dummy.users.one.routes['posts'] = Route('/posts', UserPosts())

print(api.resolve('/api/users'))
print(api.resolve('/api/users/1'))
print(api.resolve('/api/users/1/posts'))
print(api.resolve('/api/users/1/posts/2'))

request = Request('/api/users')

request['method'] = 'POST'
request['data'] = {
    'name': 'Jesse the Game',
    'age': 24,
}
#request['router'] = api

app = test.server('localhost', 333, api)

print(request)
try:
    print(str(app.resolve(request)))
except Response as response:
    print(str(response))

print(app.get('/api/users'))

#app.forever()
