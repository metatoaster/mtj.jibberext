import logging

from sqlalchemy import create_engine
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.schema import MetaData
from sqlalchemy.schema import Table
from sqlalchemy.schema import Column
from sqlalchemy.schema import Index
from sqlalchemy.types import VARCHAR

from mtj.jibber.core import Command

logger = logging.getLogger('mtj.jibberext')


class Pinger(Command):
    """
    A thing that spams nicknames of a muc into the chat.  Pinging.

    Use with utmost care.  If used with utmost uncare hilarity and lots
    of mad and tears will result.  This has been tested on test general.

    Generally (or sadistically), this can be instantiated without a
    database support.

    >>> pinger = Pinger()

    To make this less problematic, use a database, and a filter so that
    only willing victims will have their nicknames spammed into the
    channel.

    >>> pinger = Pinger('sqlite://')
    """

    def __init__(self,
            db_src=None,
            ping_msg=None,
            no_victim_msg=None,
            nick_joiner=': ',
        ):
        if db_src:
            self.engine = create_engine(db_src)
            self.initialize_db()
        else:
            logger.warning('No database defined for Pinger')
            self.engine = None

        self.ping_msg = ping_msg
        self.no_victim_msg = no_victim_msg
        self.nick_joiner = nick_joiner

    def initialize_db(self):
        if hasattr(self, '_metadata'):
            logger.info('already initialized')
            return

        metadata = MetaData(bind=self.engine)
        self.victim_nicknames = Table(u'victim_nicknames', metadata,
            Column(u'nickname', VARCHAR(length=255),
                primary_key=True, nullable=False),
        )
        self.victim_pingjids = Table(u'victim_jids', metadata,
            Column(u'jid', VARCHAR(length=255),
                primary_key=True, nullable=False),
        )
        self.victim_admins = Table(u'victim_admins', metadata,
            Column(u'admin_jid', VARCHAR(length=255),
                primary_key=True, nullable=False),
        )

        metadata.create_all()

        self._metadata = metadata

    def get_connection(self):
        try:
            return self.engine.connect()
        except Exception as e:
            logger.error('Database connect error')

    def _get_msg(self, obj, msg, match, bot):
        return callable(obj) and obj(msg=msg, match=match, bot=bot) or obj

    def _get_roster_nicknames(self, msg, match, bot):
        source_room = msg.get('mucroom', {})
        room_roster = bot.muc.rooms.get(source_room, {})
        return room_roster.keys()

    def ping_all(self, msg, match, bot, nicknames=None, **kw):
        if not nicknames:
            nicknames = self._get_roster_nicknames(msg, match, bot)
        nickstr = self.nick_joiner.join(sorted(nicknames))
        msg = self._get_msg(self.ping_msg, msg, match, bot)
        return nickstr + self.nick_joiner + msg

    # XXX these really could be hooked to a simple list overrides of sort...

    def add_victim_nickname(self, nickname):
        conn = self.get_connection()
        if conn is None:
            return
        with conn.begin():
            sql = self.victim_nicknames.insert().values(nickname=nickname)
            conn.execute(sql)

    def del_victim_nickname(self, nickname):
        conn = self.get_connection()
        if conn is None:
            return
        with conn.begin():
            sql = self.victim_nicknames.delete().where(
                self.victim_nicknames.c.nickname == nickname)
            conn.execute(sql)

    def get_victim_nicknames(self):
        conn = self.get_connection()
        if conn is None:
            return []
        sql = select([self.victim_nicknames.c.nickname])
        result = [i[0] for i in conn.execute(sql).fetchall()]
        conn.close()
        return result

    def ping_victims(self, msg, match, bot, **kw):
        victim_nicknames = set(self.get_victim_nicknames())
        roster_nicknames = set(self._get_roster_nicknames(msg, match, bot))
        nicknames = victim_nicknames & roster_nicknames
        if not nicknames:
            return self._get_msg(self.no_victim_msg, msg, match, bot)
        return self.ping_all(msg, match, bot, nicknames=nicknames)
