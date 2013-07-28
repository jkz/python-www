NAME = 'www'
VERSION = '0.0.1'
USER_AGENT = '{}/{}'.format(NAME, VERSION)

#from . import methods
from .core.exceptions import *
from .core.sexy import (
        Meta,
        Query,
        Header,
        Body,
        Request,
        Response
)
from . import (
        Query,
        Header,
        Body,
        Request,
        Response
)

