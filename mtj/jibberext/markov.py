from collections import deque

from mtj.jibber.core import Command

from mtj.markov.model import sentence
from mtj.markov.model import xmpp
from mtj.markov.graph.xmpp import XMPPGraph


class Markov(Command):
    """
    Captures the raw messages
    """

    def __init__(self, db_src):
        self.engine = XMPPGraph(db_src=db_src)
        self.engine.initialize()

    def learn(self, msg=None, match=None, bot=None, **kw):
        muc = msg['from'].bare
        nick = msg['from'].resource
        jid = bot.muc.rooms[muc][nick]['jid'].bare
        self.engine.learn({
            sentence.Loader: msg['body'],
            xmpp.Loader: {
                'muc': muc,
                'jid': jid,
                'nick': nick,
            }
        })

    def get_random_word(self, msg=None, match=None, bot=None, **kw):
        """
        Generate a random word
        """

        return self.engine.pick_word()

    def generate_random(self, msg=None, match=None, bot=None, **kw):
        """
        Generate a complete random chain.
        """

        return self.engine.generate({})

    def _generate_word(self, word):
        return self.engine.generate({'word': word})

    def generate_word(self, msg, match, bot=None, **kw):
        answer = self._generate_word(match.group('phrase'))
        if answer:
            return '%s: %s' % (msg['mucnick'], answer)

    def _generate_jid(self, jid):
        try:
            return self.engine.generate({'jid': jid})
        except:
            pass

    def generate_jid(self, msg, match, bot=None, **kw):
        answer = self._generate_jid(match.group('jid'))
        if answer:
            return '%s: %s' % (msg['mucnick'], answer)

    def mucnick_to_jid(self, muc, nick, bot):
        info = bot.muc.rooms[muc].get(nick)
        if info:
            return info['jid'].bare

    def _generate_nick(self, muc, nick, bot):
        jid = self.mucnick_to_jid(muc, nick, bot)
        if not jid:
            return '%s is not in this chat.' % nick
        return self._generate_jid(jid)

    def generate_nick_current(self, msg, match, bot, **kw):
        muc = msg['from'].bare
        nick = match.group('nick')
        answer = self._generate_nick(muc, nick, bot)
        if answer:
            return '%s: %s' % (msg['mucnick'], answer)
        return '%s has never said anything before.' % nick

    def generate_jid_or_nick(self, msg, match, bot, **kw):
        muc = msg['from'].bare
        nick = match.group('nick_or_jid')
        jid = self.mucnick_to_jid(muc, nick, bot)
        if jid is None:
            jid = nick
        answer = self._generate_jid(jid)
        if answer:
            return '%s: %s' % (msg['mucnick'], answer)
        return "%s: I don't enough about someone that goes by %s." % (
            msg['mucnick'], nick)
