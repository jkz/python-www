import unittest

from www.utils import structures

class TestMultiDict(unittest.TestCase):
    def test_add(self):
        md = structures.MultiDict()

        md.add('key', 'visible')
        self.assertEqual(md['key'], 'visible')
        md.add('key', 'invisible')
        self.assertEqual(md['key'], 'visible')

        md.add('list', [])
        self.assertEqual(md['list'], [])

    def test_items(self):
        md = structures.MultiDict()
        for i in range(4):
            md.add('key', i)

        self.assertEqual(list(md.items()), [('key', 0)])
        self.assertEqual(list(md.items(multi=True)), list(('key', i) for i in range(4)))

