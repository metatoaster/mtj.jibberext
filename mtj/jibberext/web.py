import time
import requests
import random

from mtj.jibberext.skel import PickOneFromSource


class RandomImgur(PickOneFromSource):

    def __init__(self, client_id, target,
            site_root='https://api.imgur.com/3/',
            root_data_key='data',
            requests_session=None,
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

    def get_new_items(self):
        raw = self.requests_session.get(self.site_root + self.target).json()
        return raw.get(self.root_data_key)

    def update_items(self, items):
        return items

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
