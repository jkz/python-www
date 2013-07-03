import unittest

from www.server.routes import Route, Int, Ints

class TestRoute(unittest.TestCase):
    def test_basic(self):
        api = Route('/api', 'Api',
            users = Route('/users', 'User.All',
                one = Route('/{uid}', 'User.One', uid=Int(),
                    posts = Route('/posts', 'UserPosts.All')),
                few = Route('/{uids}', 'User.Few', uids=Ints())),
            posts = Route('/posts', 'Post.All',
                few = Route('/{uids}', 'User.Few', uids=Ints()),
                one = Route('/{uid}', 'Post.One', uid=Int()),
            ))

        self.assertEqual(api.reverse(),
                         '/api')
        self.assertEqual(api.reverse('users'),
                         '/api/users')
        self.assertEqual(api.reverse('users.one', uid=123),
                         '/api/users/123')
        self.assertEqual(api.reverse('users.one.posts', uid=123),
                         '/api/users/123/posts')
        self.assertEqual(api.reverse('users.few', uids=(123, 456)),
                         '/api/users/123;456')
        self.assertEqual(api.reverse('users', uid=123),
                         '/api?uid=123')


        self.assertEqual(api.resolve('/api'),
                        ('Api', {}))
        self.assertEqual(api.resolve('/api/users'),
                        ('User.All', {}))
        self.assertEqual(api.resolve('/api/users/123'),
                        ('User.One', {'uid': 123}))
        self.assertEqual(api.resolve('/api/users/123;456'),
                        ('User.Few', {'uids': (123, 456)}))

    def test_order(self):
        #XXX Predictable unwanted behaviour. Meh.
        right = Route('',
                true = Route('/same', True),
                false = Route('/same', False))

        wrong = Route('',
                true = Route('/same', True),
                false = right.false)

        self.assertEqual(right.resolve('/same'), (True, {}))
        self.assertEqual(wrong.resolve('/same'), (False, {}))
