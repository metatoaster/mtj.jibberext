from collections import deque

from mtj.jibber.core import Command


class Monitor(Command):
    """
    Captures the raw messages
    """

    def __init__(self, maxlen=32):
        self.items = deque(maxlen=maxlen)

    def listen(self, msg=None, match=None, bot=None, **kw):
        self.items.append(msg)
