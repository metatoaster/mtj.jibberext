import logging
import time
import requests
import random
from xml.etree import ElementTree

from mtj.jibber.core import Command
from mtj.jibberext.skel import PickOneFromSource

logger = logging.getLogger(__name__)

try:
    from youtube_dl import YoutubeDL
except ImportError:
    logger.info('youtube_dl is not available')
    YoutubeDL = None


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


class VideoInfo(Command):
    """
    Fetches video info.  Currently we do title by default.  Uses the
    ``youtube_dl`` library for all the information.

    Example configuration that fetches titles from youtube, vimeo and
    vine links::

        {
            "package": "mtj.jibberext.web.VideoInfo",
            "alias": "video_info",
            "kwargs": {
            },
            "commands": [
                ["(?P<url>http[s]?:\/\/((www.)?youtube.com|youtu.be)\/[\\w\\?=&\\-_]*|vimeo.com\/[0-9]*|vine.co\/v\/[\\w]*)",
                    "get_video_title"]
            ]
        },

    """

    def __init__(self):
        if YoutubeDL is None:
            raise RuntimeError('youtube-dl is not available')

        self.ydl = YoutubeDL()

    def extract_info(self, msg, match, bot, **kw):
        if not match:
            return {}
        gd = match.groupdict()
        url = gd.get('url')
        if not url:
            if not 'url' in gd:
                logger.warning('URL match group may be missing in pattern?')
            return {}
        info = self.ydl.extract_info(url, download=False)
        return info

    def get_video_title(self, msg, match, bot, **kw):
        info = self.extract_info(msg, match, bot, **kw)
        return info.get('title')


class YoutubeComment(Command):
    """
    Why???

        {
            "package": "mtj.jibberext.web.YoutubeComment",
            "alias": "youtube_comment",
            "kwargs": {
            },
            "commands": [
                ["http[s]?:\/\/(www.)?youtube.com\/[^\\s]*v=(?P<video_id>[\\w\\-_]*)",
                    "pick_comment"],
                ["http[s]?:\/\/youtu.be\/(?P<video_id>[\\w\\-_]*)",
                    "pick_comment"]
            ]
        },

    Okay this will pull a random comment from a video link.  I hope you
    have eye bleach.
    """

    def __init__(self, max_results=50):
        self.cache = {}
        self.max_results = max_results
        self.requests_session = requests.Session()

    def fetch_comments(self, vid):
        if vid in self.cache:
            return self.cache.get(vid)

        r = self.requests_session.get(
            'https://gdata.youtube.com/feeds/api/videos/'
            '%s/comments?max-results=%d' % (vid, self.max_results))
        if r.status_code >= 400:
            return []

        et = ElementTree.fromstring(r.content)

        self.cache[vid] = [n.text for n in et.findall(
            './atom:entry/atom:content',
            {'atom': 'http://www.w3.org/2005/Atom'})
        ]
        return self.cache.get(vid)

    def pick_comment(self, msg, match, bot, **kw):
        if not match:
            return

        gd = match.groupdict()
        vid = gd.get('video_id')
        if not vid:
            return

        comments = self.fetch_comments(vid)
        if comments:
            return random.choice(comments)
