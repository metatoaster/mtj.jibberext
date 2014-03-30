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


class Unping(object):

    def __init__(self, s, rep='_'):
        self.s = s
        self.rep = rep

    def __str__(self):
        return self.s[:-1] + self.rep


class Relay(Command):
    """
    Captures raw message from a source and relays to target.
    """

    def __init__(self, source, target, format_str=None):
        """
        Extra keywords will be passed to messages.
        """

        self.source = source
        self.target = target
        self.format_str = format_str

    def format_msg(self, msg):
        if not self.format_str:
            return msg['body']

        if '{mucnick_}' in self.format_str:
            msg[u'mucnick_'] = Unping(msg.get('mucnick'))
        return self.format_str.format(**msg)

    def relay(self, msg=None, match=None, bot=None, **kw):
        if not str(msg['from']).startswith(self.source):
            return

        new_msg = {}
        new_msg['mto'] = self.target

        if self.target in bot.muc.rooms:
            new_msg['mtype'] = 'groupchat'

        new_msg['raw'] = self.format_msg(dict(msg))
        return new_msg
