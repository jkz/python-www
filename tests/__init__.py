import unittest

suite = unittest.TestSuite(
    unittest.TestLoader().discover('tests', 'test*.py'),
)

def run():
    return unittest.TextTestRunner(verbosity=2).run(suite)

