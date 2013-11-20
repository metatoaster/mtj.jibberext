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
            **kw
        ):
        super(RandomImgur, self).__init__(**kw)
        self.client_id = client_id
        self.target = target
        self.site_root = site_root
        self.root_data_key = root_data_key
        self.format_msg = format_msg

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Authorization': 'Client-ID ' + self.client_id,
            })
        self.requests_session = requests_session

    def update_items(self):
        raw = self.requests_session.get(self.site_root + self.target).json()
        return raw.get(self.root_data_key)

    def play(self, msg, match, **kw):
        self.refresh()
        result = random.choice(self.items)
        return self.format_msg % result % msg
