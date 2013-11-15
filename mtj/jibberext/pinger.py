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

logger = logging.getLogger(__name__)


class Pinger(Command):
    """
    A thing that spams nicknames of a muc into the chat.  Pinging.

    Use with utmost care.  If used with utmost uncare hilarity and lots
    of mad and tears will result.  This has been tested on test general.

    Generally (or sadistically to the room(s) that this module will be
    in), this can be instantiated without a database support.

    >>> pinger = Pinger()

    To make this less problematic (so mods don't start waving their
    banhammers), use a database to enable a persistent white list of
    victims.

    >>> pinger = Pinger('sqlite://')
    """

    def __init__(self,
            db_src=None,
            ping_msg=None,
            no_victim_msg=None,
            nick_joiner=': ',
        ):
        self.tables = {}

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
        self.tables['victim_nicknames'] = Table(u'victim_nicknames', metadata,
            Column(u'nickname', VARCHAR(length=255),
                primary_key=True, nullable=False),
        )
        self.tables['victim_jids'] = Table(u'victim_jids', metadata,
            Column(u'jid', VARCHAR(length=255),
                primary_key=True, nullable=False),
        )
        self.tables['admin_jids'] = Table(u'admin_jids', metadata,
            Column(u'jid', VARCHAR(length=255),
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

    def _build_add_del_get_table(table_key, value_key):
        def add_(self, value):
            table = self.tables.get(table_key)
            conn = self.get_connection()
            if conn is None:
                return
            with conn.begin():
                sql = table.insert().values(**{value_key: value})
                conn.execute(sql)

        def del_(self, value):
            table = self.tables.get(table_key)
            conn = self.get_connection()
            if conn is None:
                return
            with conn.begin():
                sql = table.delete().where(
                    table.c.get(value_key) == value)
                conn.execute(sql)

        def get_(self):
            table = self.tables.get(table_key)
            conn = self.get_connection()
            if conn is None:
                return []
            sql = select([table.c.get(value_key)])
            result = [i[0] for i in conn.execute(sql).fetchall()]
            conn.close()
            return result

        return add_, del_, get_

    add_victim_nickname, del_victim_nickname, get_victim_nicknames = \
        _build_add_del_get_table('victim_nicknames', 'nickname')

    add_victim_jid, del_victim_jid, get_victim_jids = \
        _build_add_del_get_table('victim_jids', 'jid')

    add_admin_jid, del_admin_jid, get_admin_jids = \
        _build_add_del_get_table('admin_jids', 'jid')

    def ping_victims(self, msg, match, bot, **kw):
        victim_nicknames = set(self.get_victim_nicknames())
        roster_nicknames = set(self._get_roster_nicknames(msg, match, bot))
        nicknames = victim_nicknames & roster_nicknames
        if not nicknames:
            return self._get_msg(self.no_victim_msg, msg, match, bot)
        return self.ping_all(msg, match, bot, nicknames=nicknames)
