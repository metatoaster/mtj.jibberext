import time

from mtj.jibber.bot import PickOne


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

    def update_items(self):
        raise NotImplementedError

    def refresh(self):
        if time.time() < self._next_refresh:
            return
        self.update_items()
        self._next_refresh = time.time() + self.timeout
