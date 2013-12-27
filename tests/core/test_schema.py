import unittest

from www.core import schema
from www.core import fields

class Href(fields.Field):
    writable = False

    def revert(self, val):
        return '/users/{}'.format(val['id'])

class TestSchema(unittest.TestCase):
    def test_schema(self):
        thing = schema.Object(
            id = fields.Integer(writable=True),
            name = fields.String(writable=True),
            href = Href(alias=False),
        )

        person = thing + schema.Object(
            friends = fields.Array(
                Href(),
                writable = False,
            ),
        )

        quote = thing + schema.Object(
            text = fields.String(writable=True),
            person = fields.Object(person),
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

        sorry = {
            'id': 10,
            'name': 'Sorry',
            'person': sam,
            'text': 'Sorry mister Frodo',
        }

        tricksed = {
            'id': 11,
            'name': 'Tricksed',
            'person': smeagol,
            'text': 'Tricksed us?!',
        }

