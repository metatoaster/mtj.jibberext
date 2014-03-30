from unittest import TestCase

from mtj.jibberext.utility import Monitor
from mtj.jibberext.utility import Relay

class FakeMuc(object):

    def __init__(self, rooms):
        self.rooms = rooms

class FakeBot(object):

    def __init__(self, rooms):
        self.muc = FakeMuc(rooms)


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


class RelayTestCase(TestCase):

    def test_relay_setup(self):
        relay = Relay('source@chat.example.com', 'dest@chat.example.com')
        self.assertTrue(relay.source.startswith('source'))
        self.assertTrue(relay.target.startswith('dest'))

    def test_relay_run_not_source(self):
        bot = FakeBot({})
        relay = Relay('source@chat.example.com', 'dest@chat.example.com')
        result = relay.relay(
            msg={
                'type': 'chat',
                'body': 'This is a test message',
                'from': 'elsewhere@chat.example.com',
            },
            match=None,
            bot=bot,
        )
        self.assertIsNone(result)

    def test_relay_run_pm(self):
        bot = FakeBot({})
        relay = Relay('source@chat.example.com', 'dest@chat.example.com')
        result = relay.relay(
            msg={
                'type': 'chat',
                'body': 'This is a test message',
                'from': 'source@chat.example.com',
            },
            match=None,
            bot=bot,
        )

        self.assertEqual(result['raw'], 'This is a test message')
        self.assertIsNone(result.get('mtype'))

    def test_relay_run_muc(self):
        bot = FakeBot({'destroom@chat.example.com': {}})
        relay = Relay('source@chat.example.com', 'destroom@chat.example.com')
        result = relay.relay(
            msg={
                'type': 'chat',
                'body': 'This is a test message',
                'from': 'source@chat.example.com',
            },
            match=None,
            bot=bot,
        )

        self.assertEqual(result['raw'], 'This is a test message')
        self.assertEqual(result['mtype'], 'groupchat')

    def test_format_message(self):
        relay = Relay('source', 'dest', '{mucnick}: {body}')
        result = relay.format_msg(
            msg={
                'type': 'groupchat',
                'body': 'This is a test message',
                'from': 'source@chat.example.com',
                'mucnick': 'A Sender',
            },
        )

        self.assertEqual(result, 'A Sender: This is a test message')

    def test_format_message_unping(self):
        relay = Relay('source', 'dest', '{mucnick_}: {body}')
        result = relay.format_msg(
            msg={
                'type': 'groupchat',
                'body': 'This is a test message',
                'from': 'source@chat.example.com',
                'mucnick': 'A Sender',
            },
        )

        self.assertEqual(result, 'A Sende_: This is a test message')
