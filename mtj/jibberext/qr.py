from qrcode import QRCode

from mtj.jibber.core import Command

_template = (
    '<html><body><span style="background:#fff;color:#000;'
    'font-family:Courier New,monospace;font-size:xx-small">'
    '<br/>%s</span></body></html>'
)

_eol = u'\xa0' * 20 + u'\n'


class FakeStream(list):
    def write(self, s):
        self.append(s)
    def flush(self):
        pass


class Code(Command):
    """
    Renders QR Codes.  Requires ``qrcode`` to be installed.

    Need a named subpattern called ``code`` to make this work.

    An example section inside the ``packages`` section::

        {
            "package": "mtj.jibberext.qr.Code",
            "kwargs": {},
            "private_commands": [
                ["^!qr (?P<code>.*)$", "render"]
            ]
        }

    The above will provide a private_command handler whenever a private
    message is sent to the bot beginning with ``!qr `` and whatever
    following that will be matched and placed into the code group, which
    the ``render`` method will process and then the QR code will be
    generated and returned.

    Arguments

    max_length
        The maximum character length that will be interpreted.  The
        ``render`` method will ignore matched code greater than this.
        Default: 64

    template
        Optional.  Default should be good enough.  See source code for
        details.

    eol
        Optional.  This is the string that will replace the newline in
        the string, and pad out the ending with enough spaces to flow
        the next line onto the next line on typical graphical clients.
        Normal newlines will result in a gap which will confuse QR Code
        readers.

    errmsg_too_long
        Set the desired too long message.
    """

    def __init__(self, max_length=64, template=_template, eol=_eol,
            errmsg_too_long='Input text is too long (max characters: {0}).'):
        self.max_length = max_length
        self.template = template
        self.eol = eol
        self.errmsg_too_long = errmsg_too_long

    def render(self, msg=None, match=None, bot=None, **kw):
        code = match.groupdict().get('code', '')
        if not code:
            return
        if len(code) > self.max_length:
            return self.errmsg_too_long.format(self.max_length)

        return self.make_code(code)

    def make_code(self, code):
        q = QRCode()
        q.add_data(code)
        stream = FakeStream()
        q.print_ascii(stream)
        return self.template % u''.join(stream).replace('\n', self.eol)
