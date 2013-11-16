from unittest import TestCase, skipIf

from mtj.jibberext.pinger import Pinger


class Muc(object):
    def __init__(self, rooms):
        self.rooms = rooms


class FakeBot(object):

    def __init__(self, rooms):
        self.muc = Muc(rooms)

bot = FakeBot({
    'room@chat.example.com': {
        'userA': {'jid': 'usera@example.com'},
        'userB': {'jid': 'userb@example.com'},
        'userC': {'jid': 'userc@example.com/fail'},
        'userD': {'jid': 'userd@example.com/fail', 'role': 'moderator'},
        'userE': {'jid': 'usere@example.com', 'affiliation': 'owner'},
    },
    'house@chat.example.com': {
        'userA': {'jid': 'usera@example.com'},
        'userC': {'jid': 'userc@example.com/fail'},
        'userE': {'jid': 'usere@example.com'},
    },
    'kitchen@chat.example.com': {
        'tester 1': {'jid': 'tester1@example.com/derp'},
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

    def test_victim_jids(self):
        pinger = Pinger(db_src='sqlite://')
        pinger.add_victim_jid('tester1@example.com')
        self.assertEqual(sorted(pinger.get_victim_jids()),
            ['tester1@example.com'])
        pinger.add_victim_jid('tester2@example.com')
        self.assertEqual(sorted(pinger.get_victim_jids()),
            ['tester1@example.com', 'tester2@example.com'])
        pinger.del_victim_jid('tester1@example.com')
        self.assertEqual(sorted(pinger.get_victim_jids()),
            ['tester2@example.com'])

    def test_victim_jids_no_db(self):
        pinger = Pinger()
        pinger.add_victim_jid('tester1@example.com')
        self.assertEqual(pinger.get_victim_jids(), [])
        pinger.del_victim_jid('tester1@example.com')
        self.assertEqual(pinger.get_victim_jids(), [])

    # pinging functions

    def test_pingall(self):
        pinger = Pinger(msg_ping='hi')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, 'userA: userB: userC: userD: userE: hi')

    def test_pingall_callable(self):
        def caller(msg, match, bot):
            # return as is...
            return match
        pinger = Pinger(msg_ping=caller)
        msg = {'mucroom': 'house@chat.example.com'}
        # even though match is normally a regex match result...
        result = pinger.ping_all(msg, 'not a match object', bot)
        self.assertEqual(result, 'userA: userC: userE: not a match object')

    def test_ping_victim_timeout(self):
        pinger = Pinger(db_src='sqlite://',
            msg_ping='hi', msg_no_victim='I see no victims.')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, None)

    # ping and db

    def test_ping_victim_nicknames_only(self):
        pinger = Pinger(db_src='sqlite://', timeout_victim_ping=0,
            msg_ping='hi', msg_no_victim='I see no victims.')
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

    def test_ping_victim_jids_only(self):
        pinger = Pinger(db_src='sqlite://', timeout_victim_ping=0,
            msg_ping='hi', msg_no_victim='I see no victims.')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_jid('tester1@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_jid('usera@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: hi')

        msg = {'mucroom': 'kitchen@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'tester 1: hi')

    def test_ping_victim_jids_nicknames_mix(self):
        pinger = Pinger(db_src='sqlite://', timeout_victim_ping=0,
            msg_ping='hi', msg_no_victim='I see no victims.')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_jid('tester1@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'I see no victims.')

        pinger.add_victim_jid('usera@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: hi')

        pinger.add_victim_nickname('userA')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: hi')

        msg = {'mucroom': 'kitchen@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'tester 1: hi')

        pinger.add_victim_nickname('tester 1')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'tester 1: hi')

        msg = {'mucroom': 'room@chat.example.com'}

        pinger.add_victim_jid('userb@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: userB: hi')

        pinger.add_victim_nickname('userc@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: userB: hi')

        pinger.add_victim_jid('userc@example.com')
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'userA: userB: userC: hi')

    def test_ping_no_victim_no_msg(self):
        pinger = Pinger(db_src='sqlite://')
        msg = {'mucroom': 'room@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, None)
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, None)

    def test_ping_with_callable_msg(self):
        def call(msg, match, bot, **kw):
            return {'raw': 'call result.'}

        pinger = Pinger(db_src='sqlite://', msg_no_victim=call,
            msg_ping=call)
        msg = {'mucroom': 'house@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, {'raw': 'call result.'})
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, {'raw': 'userA: userC: userE: call result.'})

    def test_ping_with_no_msg(self):
        pinger = Pinger(db_src='sqlite://')
        msg = {'mucroom': 'house@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, None)
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, None)

    def test_ping_format(self):
        def call(msg, match, bot, **kw):
            return {'raw': '%(mucnick)s: nope.avi'}
        pinger = Pinger(db_src='sqlite://', msg_no_victim=call,
            msg_ping='blame %(mucnick)s.')
        msg = {'mucnick': 'tester', 'mucroom': 'house@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, {'raw': 'tester: nope.avi'})
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, 'userA: userC: userE: blame tester.')

    def test_ping_format_reversed(self):
        def call(msg, match, bot, **kw):
            return {'raw': 'blame %(mucnick)s.'}
        pinger = Pinger(db_src='sqlite://', msg_ping=call,
            msg_no_victim='%(mucnick)s: nope.avi')
        msg = {'mucnick': 'tester', 'mucroom': 'house@chat.example.com'}
        result = pinger.ping_victims(msg, None, bot)
        self.assertEqual(result, 'tester: nope.avi')
        result = pinger.ping_all(msg, None, bot)
        self.assertEqual(result, {'raw': 'userA: userC: userE: blame tester.'})

    def test_ping_with_bad_msg(self):
        pinger = Pinger(db_src='sqlite://', msg_ping={'raw': object})
        msg = {'mucnick': 'tester', 'mucroom': 'house@chat.example.com'}
        result = pinger.ping_all(msg, None, bot)
        self.assertTrue(result['raw'].startswith('userA: '))

    def test_bad_get_msg_template(self):
        _marker = object()
        pinger = Pinger()
        result = pinger._get_msg({'raw': _marker}, '', None, bot,
            template=_marker)
        self.assertEqual(result['raw'], '')

        _marker = object()
        pinger = Pinger()
        result = pinger._get_msg({'fail': 'fail'}, '', None, bot,
            template=_marker)
        self.assertEqual(result, {'fail': 'fail'})

    def test_is_admin(self):
        pinger = Pinger(db_src='sqlite://')
        msg = {'mucnick': 'userA', 'mucroom': 'room@chat.example.com',
            'from': 'somewhere',}
        roster = pinger._get_roster(msg, None, bot)
        self.assertFalse(pinger.is_admin(roster=roster, **msg))
        self.assertFalse(pinger.is_admin(jid='usera@example.com'))

        pinger.add_admin_jid('usera@example.com')
        self.assertTrue(pinger.is_admin(roster=roster, **msg))
        self.assertTrue(pinger.is_admin(jid='usera@example.com'))

        # private message.
        msg = {'from': 'usera@example.com/home'}
        self.assertTrue(pinger.is_admin(**msg))

        pinger.del_admin_jid('usera@example.com')
        self.assertFalse(pinger.is_admin(jid='usera@example.com'))

        # default affiliation/role
        msg = {'mucnick': 'userD', 'mucroom': 'room@chat.example.com',
            'from': 'somewhere',}
        self.assertTrue(pinger.is_admin(roster=roster, **msg))

        msg = {'mucnick': 'userE', 'mucroom': 'room@chat.example.com',
            'from': 'somewhere',}
        self.assertTrue(pinger.is_admin(roster=roster, **msg))

    def test_ping_subscription(self):
        pinger = Pinger(db_src='sqlite://')
        msg = {'mucnick': 'userA', 'mucroom': 'room@chat.example.com',
            'from': 'somewhere', 'type': 'groupchat'}
        self.assertTrue(pinger.pm_subscribe_victim(msg, None, bot) is None)
        self.assertTrue(pinger.pm_unsubscribe_victim(msg, None, bot) is None)

        msg = {'from': 'usera@example.com/home', 'type': 'chat'}
        result = pinger.pm_subscribe_victim(msg, None, bot)
        self.assertEqual(result['raw'],
            'You are now subscribed to the Pinger.')
        self.assertEqual(pinger.get_victim_jids(), ['usera@example.com'])

        result = pinger.pm_subscribe_victim(msg, None, bot)
        self.assertEqual(result['raw'],
            'You are already subscribed.')

        result = pinger.pm_unsubscribe_victim(msg, None, bot)
        self.assertEqual(result['raw'],
            'You are now unsubscribed to the Pinger.')
        self.assertEqual(pinger.get_victim_jids(), [])

        result = pinger.pm_unsubscribe_victim(msg, None, bot)
        self.assertEqual(result['raw'],
            'You are already unsubscribed.')
