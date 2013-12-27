import unittest

from www.core import exceptions
from www.server import stack
from www.server import responses

class TestStack(unittest.TestCase):
    def test_build(self):
        pass


    def test_serialize(self):
        pass


    def test_deserialize(self):
        pass


    def test_router(self):
        pass


    def test_excepts(self):
        Success = responses.NoContent()

        def returner(request):
            return Success

        def raiser(request):
            raise Success

        def fault(request):
            raise exceptions.Fault

        def error(request):
            raise exceptions.Error

        def warning(request):
            raise exceptions.Warning

        def exception(request):
            raise Exception


        self.assertEqual(stack.Excepts(returner)(None), Success)
        self.assertEqual(stack.Excepts(raiser)(None), Success)
        for app in fault, error, warning, exception:
            self.assertEqual(isinstance(stack.Excepts(app)(None),
                responses.InternalServerError), True)
