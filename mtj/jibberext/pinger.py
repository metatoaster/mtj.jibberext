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
            nick_joiner=': ',
            stanza_admin_conditions=(
                ('affiliation', ['owner']),
                ('role', ['moderator']),
            ),

            msg_ping=None,
            msg_no_victim=None,

            msg_subscribed='You are now subscribed to the Pinger.',
            msg_already_subscribed='You are already subscribed.',
            msg_unsubscribed='You are now unsubscribed to the Pinger.',
            msg_already_unsubscribed='You are already unsubscribed.',
        ):
        self.tables = {}

        if db_src:
            self.engine = create_engine(db_src)
            self.initialize_db()
        else:
            logger.warning('No database defined for Pinger')
            self.engine = None

        self.msg_ping = msg_ping
        self.msg_no_victim = msg_no_victim
        self.nick_joiner = nick_joiner
        self.stanza_admin_conditions = stanza_admin_conditions

        self.msg_subscribed = msg_subscribed
        self.msg_already_subscribed = msg_already_subscribed
        self.msg_unsubscribed = msg_unsubscribed
        self.msg_already_unsubscribed = msg_already_unsubscribed

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

    def _get_msg(self, obj, msg, match, bot, template=None):
        if callable(obj):
            called = obj(msg=msg, match=match, bot=bot)
        else:
            called = obj

        if template is None or called is None:
            return called

        if not isinstance(called, dict):
            return template % called % msg

        result = {}
        result.update(called)

        try:
            result['raw'] = template % result['raw'] % msg
        except:
            logger.error('could not apply result %r into template %r')
        return result

    def _get_roster(self, msg, match, bot):
        source_room = msg.get('mucroom', {})
        room_roster = bot.muc.rooms.get(source_room, {})
        return room_roster

    def _get_roster_nicknames(self, msg, match, bot):
        return self._get_roster(msg, match, bot).keys()

    def ping_all(self, msg, match, bot, nicknames=None, **kw):
        if not self.msg_ping:
            return

        if not nicknames:
            nicknames = self._get_roster_nicknames(msg, match, bot)
        nickstr = self.nick_joiner.join(sorted(nicknames))
        result = self._get_msg(self.msg_ping, msg, match, bot,
            template=(nickstr + self.nick_joiner + '%s'))
        return result

    # XXX these really could be hooked to a simple list accessor that
    # has magic methods that hooks into the database.

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

        def get_(self, value=None):
            table = self.tables.get(table_key)
            conn = self.get_connection()
            if conn is None:
                return []
            sql = select([table.c.get(value_key)])
            if value:
                sql = sql.where(table.c.get(value_key) == value)
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

    def _get_nicknames_by_jid(self, msg, match, bot):
        jids = set(self.get_victim_jids())
        room_roster = self._get_roster(msg, match, bot)
        return [nickname for nickname, details in room_roster.items()
            if str(details.get('jid', '')).split('/')[0] in jids]

    def ping_victims(self, msg, match, bot, **kw):
        victim_nicknames = set(self.get_victim_nicknames())
        jid_nicknames = set(self._get_nicknames_by_jid(msg, match, bot))
        roster_nicknames = set(self._get_roster_nicknames(msg, match, bot))
        nicknames = roster_nicknames & (victim_nicknames | jid_nicknames)
        if not nicknames:
            return self._get_msg(self.msg_no_victim, msg, match, bot)
        return self.ping_all(msg, match, bot, nicknames=nicknames)

    def is_admin(self, mucnick=None, jid=None, roster={}, **kw):
        """
        Determine from arguments whether it represents an admin.

        Typically the arguments is the entire dict object for any
        message stanzas.

        The jid argument will used if and only if the message stanza
        does not resolved to one.
        """

        details = {}
        from_ = kw.get('from', None)

        # Step 1: check the mucnick against its roster.
        if mucnick:
            rosteritem = roster.get(mucnick, {})
            for key, values in self.stanza_admin_conditions:
                if rosteritem.get(key) in values:
                    return True

            # Step 1.5: if stanza does not satisfy that condition, fall
            # back to jid.
            if jid is None:
                jid = roster.get(mucnick, {}).get('jid')
        if not jid and from_:
            jid = from_

        # Step 2: jid lookup from list of admins.
        # roster will _not_ be available in nearly all cases in how this
        # is invoked; rather the jid would have already been resolved
        # thus render that additioal lookup unnecessary.
        jid_base = str(jid).split('/')[0]
        return len(self.get_admin_jids(jid_base)) > 0

    def pm_subscribe_victim(self, msg, match, bot, **kw):
        # ensure this is a chat message
        if msg.get('type') != 'chat':
            return
        victim = str(msg.get('from')).split('/')[0]

        if self.get_victim_jids(victim):
            return {
                'mto': msg.get('from'),
                'raw': self.msg_already_subscribed,
            }

        self.add_victim_jid(victim)
        return {
            'mto': msg.get('from'),
            'raw': self.msg_subscribed,
        }

    # yay copypasta... but we may recycle this type of thing in a
    # different context, so leaving this here until it's sorted.
    def pm_unsubscribe_victim(self, msg, match, bot, **kw):
        # ensure this is a chat message
        if msg.get('type') != 'chat':
            return
        victim = str(msg.get('from')).split('/')[0]

        if not self.get_victim_jids(victim):
            return {
                'mto': msg.get('from'),
                'raw': self.msg_already_unsubscribed,
            }

        self.del_victim_jid(victim)
        return {
            'mto': msg.get('from'),
            'raw': self.msg_unsubscribed,
        }
