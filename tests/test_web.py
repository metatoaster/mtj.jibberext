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

        result = imgs.play(msg={}, match=None, bot=None)
        self.assertEqual(result[:5], 'Hello')
        self.assertEqual(result[10:13], 'url')
