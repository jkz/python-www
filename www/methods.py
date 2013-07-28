from .core import exceptions

NONE = set()
ALL = set(['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS'])
IDEMPOTENT = ALL - set(['POST', 'PATCH'])
SAFE = IDEMPOTENT - set(['PUT', 'DELETE'])
DANGEROUS = ALL - SAFE
FORM = set(['GET', 'POST'])
CRUD = set(['GET', 'POST', 'PUT', 'DELETE'])
DATA = set(['PUT', 'POST', 'PATCH'])

class Method:
    def __init__(self, verb=None, allowed=ALL):
        self.allowed = allowed
        self.verb = self.convert(verb)

    def convert(self, verb):
        if verb is not None:
            VERB = verb.upper()
            if self.allowed is not None and VERB not in self.allowed:
                raise exceptions.MethodNotAllowed(VERB)
        return verb

    def __set__(self, instance, verb):
        self.verb = self.convert(verb)

    def __get__(self, instance, owner):
        return self.verb

    def __str__(self):
        return self.verb

