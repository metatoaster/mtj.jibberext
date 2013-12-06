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
    data = (
        '{"data":['
            '{"id":"1","title":"Hello1.","description":null,"link":"url1"},'
            '{"id":"2","title":"Hello2.","description":null,"link":"url2"},'
            '{"id":"2","title":"Hello3.","description":null,"link":"url3"},'
            '{"id":"3","title":"Hello4.","description":null,"link":"url4"}'
        ']}'
    )
        
    def get(self, target, *a, **kw):
        return DummyResponse(self.data)


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
