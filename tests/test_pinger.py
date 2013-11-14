from unittest import TestCase, skipIf

from mtj.jibberext.pinger import Pinger

import tests


class Muc(object):
    def __init__(self, rooms):
        self.rooms = rooms


class FakeBot(object):

    def __init__(self, rooms):
        self.muc = Muc(rooms)

bot = FakeBot({
    'room@chat.example.com': {
        'userA': {},
        'userB': {},
        'userC': {},
        'userD': {},
        'userE': {},
    },
    'house@chat.example.com': {
        'userA': {},
        'userC': {},
        'userE': {},
    },
    'kitchen@chat.example.com': {
        'tester 1': {},
    },
})


class TestPinger(TestCase):

    def test_db(self):
        pinger = Pinger(db_src='sqlite://')
        # reinit should do nothing.
        pinger.initialize_db()

    # db functions

    def test_victim_nicknames(self):
        pinger = Pinger(db_src='sqlite://')
        pinger.add_victim_nickname('tester 1')
        self.assertEqual(sorted(pinger.get_victim_nicknames()),
            ['tester 1'])
        pinger.add_victim_nickname('tester 2')
        self.assertEqual(sorted(pinger.get_victim_nicknames()),
            ['tester 1', 'tester 2'])
        pinger.del_victim_nickname('tester 1')
        self.assertEqual(sorted(pinger.get_victim_nicknames()),
            ['tester 2'])

    def test_victim_nicknames_no_db(self):
        pinger = Pinger()
        pinger.add_victim_nickname('tester 1')
        self.assertEqual(pinger.get_victim_nicknames(), [])
        pinger.del_victim_nickname('tester 1')
        self.assertEqual(pinger.get_victim_nicknames(), [])

    # pinging functions

    def test_pingall(self):
        pinger = Pinger(ping_msg='hi')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, 'userA: userB: userC: userD: userE: hi')

    def test_pingall_callable(self):
        def caller(msg, match, bot):
            # return as is...
            return match
        pinger = Pinger(ping_msg=caller)
        msg = {'mucroom': 'house@chat.example.com'}
        # even though match is normally a regex match result...
        result = pinger.ping_all(msg, 'not a match object', bot)
        self.assertEqual(result, 'userA: userC: userE: not a match object')

    # ping and db

    def test_ping_victim_nicknames_only(self):
        pinger = Pinger(db_src='sqlite://',
            ping_msg='hi', no_victim_msg='I see no victims.')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_nickname('tester 1')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_nickname('userA')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: hi')

        msg = {'mucroom': 'kitchen@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'tester 1: hi')
