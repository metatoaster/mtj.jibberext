from unittest import TestCase
import time

from mtj.jibberext.skel import PickOneFromSource


class PickOneFromSourceTestCase(TestCase):

    def test_refresh(self):
        p1 = PickOneFromSource()
        self.assertTrue(p1.timeout > 0)
        self.assertEqual(p1._next_refresh, 0)
        self.assertRaises(NotImplementedError, p1.refresh)
        p1._next_refresh = time.time() + 100
        p1.refresh()

    def test_refresh_update(self):
        p1 = PickOneFromSource()
        p1.update_items = lambda: True
        self.assertTrue(p1.timeout > 0)
        self.assertEqual(p1._next_refresh, 0)
        p1.refresh()
        self.assertNotEqual(p1._next_refresh, 0)

    def test_items(self):
        marker = object()
        p1 = PickOneFromSource()
        p1._items = marker
        self.assertEqual(p1.items, marker)
