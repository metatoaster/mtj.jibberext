from unittest import TestCase, skipIf

from os.path import join, dirname

from mtj.jibberext import fortune
from mtj.jibberext import _fortune


def path(name):
    return join(dirname(__file__), name)


@skipIf(fortune.HAS_FORTUNE, "real fortune is available")
class TestFortune(TestCase):

    def test_fortune(self):
        f = fortune.Fortune(path('fortunes'))
        self.assertEqual(len(_fortune._fortunes), 2)
        result = f.fortune({'mucnick': 'Tester'}, None)
        self.assertTrue(result.startswith('Tester: Test fortune'))
