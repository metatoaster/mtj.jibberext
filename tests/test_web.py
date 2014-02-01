from unittest import TestCase
import time
import json

from mtj.jibberext.web import RandomImgur


class DummyResponse(object):
    def __init__(self, raw):
        self.raw = raw

    def json(self):
        return json.loads(self.raw)


class DummySession(object):
    data = [
        ('{"data":['
            '{"id":"1","title":"Hello1.","description":null,"link":"url1"},'
            '{"id":"2","title":"Hello2.","description":null,"link":"url2"},'
            '{"id":"3","title":"Hello3.","description":null,"link":"url3"},'
            '{"id":"4","title":"Hello4.","description":null,"link":"url4"}'
        ']}'),
        ('{"data":['
            '{"id":"4","title":"Hello4.","description":null,"link":"url4"},'
            '{"id":"5","title":"Hello1.","description":null,"link":"url1"},'
            '{"id":"6","title":"Hello2.","description":null,"link":"url2"},'
            '{"id":"7","title":"Hello3.","description":null,"link":"url3"},'
            '{"id":"8","title":"Hello4.","description":null,"link":"url4"}'
        ']}'),
        ('{"data":['
            '{"id":"7","title":"Hello2.","description":null,"link":"url2"},'
            '{"id":"8","title":"Hello3.","description":null,"link":"url3"},'
            '{"id":"9","title":"Hello4.","description":null,"link":"url4"}'
        ']}'),
    ]

    def __init__(self):
        self.history = []

    def get(self, target, *a, **kw):
        self.history.append(target)
        idx = 0
        if target[-1] in '012':
            idx = int(target[-1])
        return DummyResponse(self.data[idx])


class RandomImgurTestCase(TestCase):

    def test_session(self):
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/')
        self.assertEqual(imgs.requests_session.headers.get('Authorization'),
            'Client-ID example_client_id')

    def test_update_items(self):
        session = DummySession()
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            requests_session=session)
        imgs.refresh()
        self.assertEqual(len(imgs.items), 4)

    def test_play(self):
        session = DummySession()
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            requests_session=session)
        result = imgs.play(msg={'mucnick': 'Tester'}, match=None, bot=None)
        self.assertEqual(result[:5], 'Hello')
        self.assertEqual(result[10:13], 'url')

    def test_play_msg(self):
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            format_msg='%%(mucnick)s: %(link)s',
            format_msg_timer='%(link)s',
            format_msg_nsfw='%%(mucnick)s: %(link)s :nws:',
            format_msg_timer_nsfw='%(link)s :nws:',
        )
        imgs._next_refresh = time.time() + 3600

        # timers

        imgs._items = [{'id': '1', 'nsfw': False, 'link': 'url1'}]
        result = imgs.play(msg=None, match=None, bot=None)
        self.assertEqual(result, 'url1')

        imgs._items = [{'id': '1', 'nsfw': True, 'link': 'url1'}]
        result = imgs.play(msg=None, match=None, bot=None)
        self.assertEqual(result, 'url1 :nws:')

        # targetted

        imgs._items = [{'id': '1', 'nsfw': False, 'link': 'url1'}]
        result = imgs.play(msg={'mucnick': 'Tester'}, match=None, bot=None)
        self.assertEqual(result, 'Tester: url1')

        imgs._items = [{'id': '1', 'nsfw': True, 'link': 'url1'}]
        result = imgs.play(msg={'mucnick': 'Tester'}, match=None, bot=None)
        self.assertEqual(result, 'Tester: url1 :nws:')

    def test_paging_default(self):
        session = DummySession()
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            requests_session=session)
        imgs.refresh()
        self.assertEqual(session.history, [
            'https://api.imgur.com/3/gallery/r/ferret/',
        ])

    def test_paging_ranges(self):
        session = DummySession()
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            page_range=[0, 3],
            requests_session=session)
        imgs.refresh()
        self.assertEqual(session.history, [
            'https://api.imgur.com/3/gallery/r/ferret/time/0',
            'https://api.imgur.com/3/gallery/r/ferret/time/1',
            'https://api.imgur.com/3/gallery/r/ferret/time/2',
        ])
        self.assertEqual(len(imgs._items), 9)

    def test_paging_ranges_initial_only(self):
        session = DummySession()
        # yeah page_range is _the_ initial first get, subsequent ones
        # will just fetch from the first page.
        imgs = RandomImgur('example_client_id', 'gallery/r/ferret/',
            page_range=[1, 3],
            requests_session=session)
        imgs.refresh()
        self.assertEqual(session.history, [
            'https://api.imgur.com/3/gallery/r/ferret/time/1',
            'https://api.imgur.com/3/gallery/r/ferret/time/2',
        ])
        self.assertEqual(len(imgs._items), 6)

        imgs._next_refresh = 0
        imgs.refresh()
        # page 0 will be fetched as it's not specified.
        self.assertEqual(len(imgs._items), 9)
        self.assertEqual(session.history[-1],
            'https://api.imgur.com/3/gallery/r/ferret/
        )
