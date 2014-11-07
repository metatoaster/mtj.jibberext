from unittest import TestCase
import re
import time

from mtj.jibberext.timer import Countdown


class CountdownTestCase(TestCase):

    def test_bad_init(self):
        self.assertRaises(TypeError, Countdown, 'test')

    def test_extract_values(self):
        c = Countdown({'test': [12, 'before', 'now', 'after']})
        self.assertEqual(c._extract_values('test'),
            (12, 'before', 'now', 'after'))

        c = Countdown({'test': [12, 'before', 'now',]})
        self.assertEqual(c._extract_values('test'),
            (12, 'before', 'now', 'now'))

        c = Countdown({'test': [12, 'before',]})
        self.assertEqual(c._extract_values('test'),
            (12, 'before', None, None))

        c = Countdown({'test': [12,]})
        self.assertEqual(c._extract_values('test'),
            (12, None, None, None))

    def test_countdown(self):
        c = Countdown({'target': [100,
            'It is %(counter)s before target.',
            'Target is now.',
            'It is %(counter)s after target.'
        ]})

        self.assertEqual(c._countdown('target', {}, 99),
            'It is 1 second before target.')
        self.assertEqual(c._countdown('target', {}, 100),
            'Target is now.')
        self.assertEqual(c._countdown('target', {}, 102),
            'It is 2 seconds after target.')

    def test_countdown_3_tuple(self):
        c = Countdown({'target': [100,
            'It is %(counter)s before target.',
            'Target is now.',
        ]})

        self.assertEqual(c._countdown('target', {}, 99),
            'It is 1 second before target.')
        self.assertEqual(c._countdown('target', {}, 100),
            'Target is now.')
        self.assertEqual(c._countdown('target', {}, 102),
            'Target is now.')

    def test_main_countdown(self):
        regexp = re.compile('!(?P<timer_name>.*)')
        c = Countdown({
            '1B': [1000000000,
                '1 billion unix timestamp in %(counter)s.',
                '1 billion unix timestamp is now.',
                '1 billion unix timestamp was %(counter)s ago.',
            ],
            '2B': [2000000000,
                '2 billion unix timestamp in %(counter)s.',
                '2 billion unix timestamp is now.',
                '2 billion unix timestamp was %(counter)s ago.',
            ],
        })

        # pretty sure system clocks are accurate and this is firmly in
        # the past.
        match = regexp.search('!1B')
        self.assertTrue(c.countdown({}, match, None
            ).startswith('1 billion unix timestamp was'))

        # well, this can change...
        match = regexp.search('!2B')
        self.assertTrue(c.countdown({}, match, None
            ).startswith('2 billion unix timestamp'))

        # we didn't define this.
        match = regexp.search('!3B')
        self.assertTrue(c.countdown({}, match, None) is None)
