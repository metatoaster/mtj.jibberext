from unittest import TestCase

from mtj.jibberext.utility import Monitor


class MonitorTestCase(TestCase):

    def test_monitor(self):
        monitor = Monitor()
        monitor.listen('msg', 'match', 'bot')
        monitor.listen('msg', 'match', 'bot')
        monitor.listen('msg', 'match', 'bot')
        self.assertEqual(len(monitor.items), 3)

    def test_monitor_limit(self):
        monitor = Monitor(maxlen=2)
        monitor.listen('msg', 'match', 'bot')
        monitor.listen('msg', 'match', 'bot')
        monitor.listen('msg', 'match', 'bot')
        self.assertEqual(len(monitor.items), 2)
