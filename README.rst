Introduction
============

A set of Commands that extend off the `mtj.jibber`_ bot module that
provide more extensive functionality that at the very least serves as
examples on how to potentially develop off that core, but also to
provide a diverse set of usable plugins that can be plugged into a bot.

.. _mtj.jibber: https://github.com/metatoaster/mtj.jibber/

.. image:: https://travis-ci.org/metatoaster/mtj.jibberext.png?branch=master
   :target: https://travis-ci.org/metatoaster/mtj.jibberext
.. image:: https://coveralls.io/repos/metatoaster/mtj.jibberext/badge.png?branch=master
   :target: https://coveralls.io/r/metatoaster/mtj.jibberext?branch=master

Useful modules requiring somewhat extensive dependencies that are used
with mtj.jibber are included here to limit the size of that package.
Also, no dependencies are specified with this package as not all classes
will be used by the users thus they can specify the required
dependencies on their installations and/or packages.

Currently we have:

- A fortunes package (requires Python port of `fortune`_)
- A pinger package (requires `sqlalchemy`_)
- An imgur image picker (requires `requests`_)
- A QR code generator (requires `qrcode`_; output uses Unicode symbols)
- A countdown tool (requires `mtj.f3u1`_)
- Other assorted utilities.

.. _fortune: https://pypi.python.org/pypi/fortune/1.0
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _requests: http://docs.python-requests.org/en/latest/
.. _qrcode: https://pypi.python.org/pypi/qrcode
.. _mtj.f3u1: https://pypi.python.org/pypi/mtj.f3u1

Further documentation to come for each of the above, but some classes
are documented at the source code level, with example configurations
that can be copied into a mtj.jibber configuration file.
