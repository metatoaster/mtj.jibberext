from __future__ import absolute_import

HAS_FORTUNE = True
try:
    import fortune
except ImportError:
    from . import _fortune as fortune
    HAS_FORTUNE = False

from mtj.jibber import bot


class Fortune(bot.Fortune):
    """
    Give a random fortune.

    fortune_file
        The fortune file.  Requires the ``fortune`` package to be
        installed.
    """

    def __init__(self, fortune_file=None):
        fortune.make_fortune_data_file(fortune_file, quiet=True)
        self._fortune = lambda: fortune.get_random_fortune(fortune_file)
