NAME = 'www'
VERSION = '0.0.1'
USER_AGENT = '{}/{}'.format(NAME, VERSION)

#from . import methods
from .core.exceptions import *
from .core.http import (
        Meta,
        Query,
        Header,
        Body,
        Request,
        Response
)

