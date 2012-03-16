import os
import json
import pygments
from pygments import token
from pygments.util import ClassNotFound
from pygments.lexers import get_lexer_for_mimetype, guess_lexer, XmlLexer
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.formatters.terminal import TerminalFormatter
from pygments.formatters.other import NullFormatter
from pygments.lexer import  RegexLexer, bygroups
from pygments.styles import get_style_by_name, STYLE_MAP
from . import solarized
from .pygson import JSONLexer
from xml.dom.minidom import parseString


DEFAULT_STYLE = 'solarized'
NO_STYLE = 'none'
AVAILABLE_STYLES = [DEFAULT_STYLE, NO_STYLE] + STYLE_MAP.keys()
FORMATTER = (Terminal256Formatter
             if '256color' in os.environ.get('TERM', '')
             else TerminalFormatter)


class HTTPLexer(RegexLexer):
    name = 'HTTP'
    aliases = ['http']
    filenames = ['*.http']
    tokens = {
        'root': [
            (r'\s+', token.Text),
            (r'(HTTP/[\d.]+\s+)(\d+)(\s+.+)', bygroups(
             token.Operator, token.Number, token.String)),
            (r'(.*?:)(.+)',  bygroups(token.Name, token.String))
    ]}


class TextFormatter(NullFormatter):
    def __init__(self, **options):
        """
        NullFormater DOES NOT HAVE self.encoding configured!
        """
        NullFormatter.__init__(self, **options)
        self.encoding = 'ascii'

class PrettyHttp(object):

    def __init__(self, style_name):
        if style_name == 'none':
            self.formatter = TextFormatter()
        else:
            if style_name == 'solarized':
                style = solarized.SolarizedStyle
            else:
                style = get_style_by_name(style_name)
            self.formatter = FORMATTER(style=style)

    def headers(self, content):
        return pygments.highlight(content, HTTPLexer(), self.formatter)

    def body(self, content, content_type):
        lexer = None
        content_type = content_type.split(';')[0]
        if 'json' in content_type:
            lexer = JSONLexer()
            try:
                # Indent the JSON data.
                content = json.dumps(json.loads(content),
                                    sort_keys=True, indent=4)
            except Exception:
                pass
        if not lexer:
            try:
                lexer = get_lexer_for_mimetype(content_type)
            except ClassNotFound:
                try:
                    lexer = guess_lexer(content)
                except ClassNotFound:
                    return content

        if lexer.name == 'XML':
            dom = parseString(content)
            content = dom.toprettyxml(indent='  ')

        return pygments.highlight(content, lexer, self.formatter)
