import time
import logging

from mtj.f3u1.units import Time
from mtj.jibber.core import Command


class Countdown(Command):
    """
    Configure with a list of things to countdown, keyed by the target
    timer's regex named match group.  Example config:

        {
            "package": "mtj.jibberext.timer.Countdown",
            "kwargs": {
                "timers": {
                    "dragon": [
                        1496984400,
                        "How to Train Your Dragon 3 comes out in %(counter)s. Release date was pushed from June 17, 2016 to June 9, 2017.",
                        "How to Train Your Dragon 3 has been released."
                    ]
                }
            },
            "commands": [
                ["!(?P<timer_name>.*)", "countdown"]
            ]
        },

    """

    def __init__(self, timers, timer_name='timer_name'):
        """
        Arguments

        timers
            The timers to be tracked provided in a dict, used by the
            `countdown` method by matching the relevant key with the
            match group identified by `timer_name`.  The value is a list
            of strings in the order of (timestamp, before, now, after),
            all values after timestamp are optional.

            If only the timestamp is provided then nothing will be
            returned.

            If all values are provided, before match all timestamps less
            than the current timestamp, now would be if both timestamps
            match, and after will be what happens after.

            If after is omitted, the result for now will also apply to
            after.

            If only before is provided, no output once timer is over.

            As for the strings, the standard items available in `msg`
            will be passed into the basic formatter.  For example:

                "It will be %(counter)s until it is over."

        timer_name
            To identify the regular expression match group for this
            instance's regex.

            Default is 'timer_name'.
        """

        if not isinstance(timers, dict):
            raise TypeError('`timers` must be a `dict` with `str` keys and '
                'tuple of compatible message results')
            # TODO: more strict key:value validation

        self.timers = timers
        self.timer_name = timer_name

    def _extract_values(self, key):
        # could be memoized by `key`.

        i = iter(self.timers[key])
        timestamp = next(i)
        before = next(i, None)
        now = next(i, None)
        after = next(i, now)

        return timestamp, before, now, after

    def _countdown(self, key, tokens, current_timestamp):
        target_timestamp, before, now, after = self._extract_values(key)
        delta = int(target_timestamp - current_timestamp)

        if delta > 0:
            s = before
        elif delta == 0:
            s = now
        else:
            s = after
            delta = abs(delta)

        # tokens are typically msg which are not `dict`, so we do this.
        items = dict(tokens)
        items['counter'] = Time(second=delta)

        return s % items

    def countdown(self, msg, match, bot, **kw):
        """
        """

        key = match.group(self.timer_name)
        if not key in self.timers:
            return

        return self._countdown(key, msg, time.time())
