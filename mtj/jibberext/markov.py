from collections import deque

from mtj.jibber.core import Command

from mtj.markov.model import sentence
from mtj.markov.model import xmpp
from mtj.markov.graph.sentence import SentenceGraph


class Markov(Command):
    """
    Captures the raw messages
    """

    def __init__(self, db_src):
        self.engine = SentenceGraph(db_src=db_src)
        self.engine.initialize([xmpp])

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
