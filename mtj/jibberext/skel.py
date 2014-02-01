import time
import logging

from mtj.jibber.bot import PickOne

logger = logging.getLogger(__name__)


class PickOneFromSource(PickOne):

    def __init__(self,
            timeout=3600,
        ):
        self.timeout = timeout
        self._next_refresh = 0
        self._items = []

    @property
    def items(self):
        return self._items

    def get_new_items(self):
        raise NotImplementedError

    def update_items(self, items):
        raise NotImplementedError

    def refresh(self):
        if time.time() < self._next_refresh:
            return
        try:
            items = self.get_new_items()
        except:
            logger.exception('error calling refresh')
            return
        self._items = self.update_items(items)
        self._next_refresh = time.time() + self.timeout
