import unittest

from . import cases

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromTestCase(cases.TestResource),
    unittest.TestLoader().loadTestsFromTestCase(cases.TestRequest),
])

def run():
    return unittest.TextTestRunner(verbosity=2).run(suite)
