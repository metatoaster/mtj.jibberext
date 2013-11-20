import time
import requests

from mtj.jibberext.skel import PickOneFromSource


class RandomImgur(PickOneFromSource):

    def __init__(self, client_id, target,
            site_root='https://api.imgur.com/3/',
            root_data_key='data',
            link_key='link',
            requests_session=None,
            **kw
        ):
        super(RandomImgur, self).__init__(**kw)
        self.client_id = client_id
        self.target = target
        self.site_root = site_root
        self.root_data_key = root_data_key
        self.link_key = link_key

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Authorization': 'Client-ID ' + self.client_id,
            })
        self.requests_session = requests_session

    def update_items(self):
        raw = self.requests_session.get(self.site_root + self.target).json()
        item = [r.get(self.link_key) for r in raw.get(self.root_data_key)]
        return [i for i in item if i is not None]
