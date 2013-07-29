from www.core import fields as f
from www.core import schema as s

from . import hateoas

"""
For resolve:
    We need something to select schemas.
    This needs to happen before the endpoint is called.

For revert:
    We need something to select schemas.
    This needs to happen before the data is called.


Some options:
    Schemas take options and conditionals
    Schemas are combined by something else
    Schemas should be composable at field granularity

Some options:
    Schemas take options and conditionals
    Schemas are combined by something else
    Schemas should be composable at field granularity

"""

def entity(api, resource):
    return s.Object(
        uid = f.Integer(
            writable = False,
        ),
        href = hateoas.One(
            resource = resource,
            router = api.router,
        ),
    )

def collection(api, resource):
    return s.Tuple(
        f.Array(entity),
        s.Object(
            href = hateoas.All(
                resource = resource,
                router = api.router,
            ),
            next = f.String(required=False, writable=False),
            prev = f.String(required=False, writable=False),
            count = f.Integer(
                writable = False,
                revert = lambda self, value: resource.count(value),
            )
        )
    )


