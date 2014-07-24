from unittest import TestCase
import time
import re

from mtj.jibberext.qr import Code
from mtj.jibberext.qr import FakeStream


class FakeStreamTestCase(TestCase):

    def test_write(self):
        s = FakeStream()
        s.write('a')
        self.assertEqual(s, ['a'])

    def test_flush(self):
        s = FakeStream()
        s.flush()  # does nothing but doesn't fail.
        self.assertEqual(s, [])


class CodeTestCase(TestCase):

    def test_create(self):
        c = Code(max_length=64, template=u'%s', eol=u'EOL')
        self.assertEqual(c.max_length, 64)
        self.assertEqual(c.template, u'%s')
        self.assertEqual(c.eol, u'EOL')

    def test_make_code(self):
        c = Code(max_length=64, template=u'[%s]', eol=u'EOL\n')
        lines = c.make_code('a').splitlines()
        # test that the padding is rendered.
        self.assertEqual(lines[0], u'[' + u'\xa0' * 29 + 'EOL')
        self.assertEqual(lines[-1], u']')

    def test_render(self):
        patt = re.compile('(?P<code>.*)')
        c = Code(max_length=32, template=u'[%s]', eol=u'EOL\n')
        self.assertIsNone(
            c.render(msg=None, match=patt.search(u'a' * 33), bot=None))
        self.assertIsNone(
            c.render(msg=None, match=patt.search(u''), bot=None))
        self.assertIsNotNone(
            c.render(msg=None, match=patt.search(u'a'), bot=None))
