from www.rest.route import crud
from www.server.route import Route

from . import dummy

class User(dummy.Dummy):
    pass

class Post(dummy.Dummy):
    pass

class UserPosts(dummy.Dummy):
    pass

api = Route('/api',
    users = crud('/users', User),
    posts = crud('/posts', Post),
)
api.users.one.routes['posts'] = crud('/posts', UserPosts)

print(api.resolve('/users'))
