from unittest import TestCase
import time

from mtj.jibberext.skel import PickOneFromSource


class PickOneFromSourceTestCase(TestCase):

    def test_update_items(self):
        p1 = PickOneFromSource()
        self.assertRaises(NotImplementedError, p1.get_new_items)
        self.assertRaises(NotImplementedError, p1.update_items, [])

    def test_refresh_failure(self):
        p1 = PickOneFromSource()
        self.assertTrue(p1.timeout > 0)
        self.assertEqual(p1._next_refresh, 0)
        p1.refresh()
        # failure happened.
        self.assertEqual(p1._next_refresh, 0)

    def test_refresh_update(self):
        marker = object()
        class T(PickOneFromSource):
            def get_new_items(self):
                return marker
            def update_items(self, item):
                self._items = item
        p1 = T()
        self.assertTrue(p1.timeout > 0)
        self.assertEqual(p1._next_refresh, 0)
        p1.refresh()
        self.assertNotEqual(p1._next_refresh, 0)
        self.assertEqual(p1.items, marker)

        # not update due to timeout
        p1._items = None
        p1.refresh()
        self.assertIsNone(p1.items)
