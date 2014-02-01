import time
import requests
import random

from mtj.jibber.core import Command
from mtj.jibberext.skel import PickOneFromSource


class RandomImgur(PickOneFromSource):

    def __init__(self, client_id,
            target,
            site_root='https://api.imgur.com/3/',
            root_data_key='data',
            requests_session=None,
            page_key='time/%d',
            page_range=None,  # (0, 3),
            format_msg='%(title)s - %(link)s',
            format_msg_nsfw=':nsfw: %(title)s - %(link)s :nsfw:',
            format_msg_timer=None,
            format_msg_timer_nsfw=None,
            **kw
        ):
        super(RandomImgur, self).__init__(**kw)
        self.client_id = client_id
        self.target = target
        self.site_root = site_root
        self.root_data_key = root_data_key
        self.page_key = page_key
        self.page_range = page_range
        self.format_msg = format_msg
        self.format_msg_timer = format_msg_timer
        self.format_msg_nsfw = format_msg_nsfw or format_msg
        self.format_msg_timer_nsfw = format_msg_timer_nsfw or format_msg_timer

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Authorization': 'Client-ID ' + self.client_id,
            })
        self.requests_session = requests_session

        self._keys = set()

    def _get_new_items(self, target):
        raw = self.requests_session.get(target).json()
        return raw.get(self.root_data_key)

    def get_new_items(self):
        target = self.site_root + self.target
        if not self.page_range or self._items:
            return self._get_new_items(target)

        results = []
        for i in range(*self.page_range):
            results.extend(self._get_new_items(target + self.page_key % i))
        return results

    def update_items(self, items):
        if self._items is None:
            self._items = []

        for item in items:
            if item['id'] in self._keys:
                continue
            self._keys.add(item['id'])
            self._items.append(item)

    def play(self, msg=None, match=None, **kw):
        self.refresh()
        result = random.choice(self.items)

        if msg:
            format_msg = (result.get('nsfw') and
                self.format_msg_nsfw or self.format_msg)
            return format_msg % result % msg
        else:
            format_msg = (result.get('nsfw') and
                self.format_msg_timer_nsfw or self.format_msg_timer)
            return format_msg % result
