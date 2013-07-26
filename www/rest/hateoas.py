from www.core import fields as f
from www.core import schema as s

class Href(f.String):
    resource = None
    router = None
    writable = False
    alias = False

    def revert(self, value):
        return self.router.reverse(self.resource.name)

class One(Href):
    def revert(self, value):
        return self.router.reverse(
                self.resource.name + '.one',
                uid=resource.identify(value)
        )


class Few(Href):
    def revert(self, value):
        return self.router.reverse(
                self.resource.name + '.few',
                uids=tuple(resource.identify(v) for v in value),
        )

class All(Href):
    pass

