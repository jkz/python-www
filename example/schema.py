from www.core import fields as f
from www.core import schema as s

class Href(f.String):
    resource = None
    router = None
    writable = False
    alias = False

    def revert(self, value):
        return self.router.reverse(self.resource.name)

class OneHref(Href):
    def revert(self, value):
        return self.router.reverse(
                self.resource.name + '.one',
                uid=resource.identify(value)
        )


def entity(api, resource):
    return s.Object(
        uid = f.Integer(
            writable = False,
        ),
        name = f.String(),
        href = OneHref(
            resource = resource,
            router = api.router,
        ),
    )

def collection(api, resource):
    return s.Tuple(
        f.Array(entity),
        s.Object(
            href = Href(
                resource = resource,
                router = api.router,
            ),
            next = f.String(required=False, writable=False),
            prev = f.String(required=False, writable=False),
            count = f.Integer(writable=False),
        )
            count = f.Integer(
                writable = False,
                revert = lambda self, value: resource.count(value),
            )
    )
)

