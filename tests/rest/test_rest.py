import unittest

from www.core import fields
from www.core import schema

class Href(fields.Field):
    writable = False

    def value(self, val):
        return '/users/{}'.format(val['id'])

class SchemaTestCase(unittest.TestCase):
    def test_schema(self):
        base = schema.Object(
            id = fields.Integer(writable=True),
            name = fields.String(writable=True),
            href = Href(alias=False),
        )

        extra = base + schema.Object(
            friends = fields.Array(
                Href()
            ),
        )

        sam = {
            'id': 1,
            'name': 'Sam',
            'friends': [],
        }

        frodo = {
            'id': 2,
            'name': 'Frodo',
            'friends': [sam],
        }

        smeagol = {
            'id': 3,
            'name': 'Smeagol',
            'friends': [sam, frodo],
        }

        print(extra.reverse(sam))
        print(extra.reverse(frodo))
        print(extra.reverse(smeagol))

        print(extra.resolve(sam))
        print(extra.resolve(frodo))
        print(extra.resolve(smeagol))

