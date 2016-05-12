from html_template_parser.error import *
from html_template_parser.lexem import Lexem, keywords, symbols

__all__ = [
    'Tokenizer',
    'Token'
]


def is_number(str):
    return str.replace('.', '', 1).isdigit()


def is_whitespace(token):
    return token.id == 44


class Token:
    def __init__(self, id, content=None, line=None, position=None):
        self.id = id
        self.content = content
        self.line = line
        self.position = position

    def __eq__(self, other):
        return self.id == other.id and self.content == other.content


class Tokenizer:
    """Class generates tokens based on source_controller input stream."""

    def __init__(self, input_stream):
        self._source_controller = SourceController(input_stream)
        self._is_template = False
        self._is_comment = False
        self._template_end_token_id = None
        self._read_source = ''

    def get_tokens(self, omit_whitespace=False):
        """Token generator. Can omit whitespaces if argument whitespace is False"""
        token = self.get_next_token(omit_whitespace)
        while token.id is not Lexem.EOI:
            yield token
            token = self.get_next_token(omit_whitespace)

    def get_next_token(self, omit_whitespace=False):
        if self.is_end():
            line, position = self.get_current_position()
            return Token(Lexem.EOI, line=line, position=position)

        line, position = self.get_current_position()
        if self._is_template:
            token = self._get_template_token()
        else:
            token = self._get_html_token()

        if omit_whitespace and is_whitespace(token):
            return self.get_next_token(omit_whitespace)
        else:
            token.line = line
            token.position = position
            return token

    def is_end(self):
        return bool(not self._read_source and not self._source_controller.has_char())

    def get_current_position(self):
        line = self._source_controller.line_number + int(self._source_controller.line_number == 0)
        position = self._source_controller.position_number - len(self._read_source) + 1
        return line, position

    def _get_next_char(self):
        """First, reads from _read_source than from _source_controller.
        If no input left, returns empty string: ''."""
        if self._read_source:
            char = self._read_source[0]
            self._read_source = self._read_source[1:]
        else:
            char = self._source_controller.get_char()
        return char

    def _get_html_token(self):
        """Returns HTML token. When template opening bracket is found,
        place it in _read_source."""
        content = ''
        while not self.is_end() and not self._is_template_opener_in(content):
            content += self._get_next_char()

        if self._is_template_opener_in(content):
            self._read_source = content[-2:] + self._read_source
            self._is_template = True
            self._template_end_token_id = symbols[content[-2:]] + 1
            content = content[:-2]
        if content is '':
            return self._get_template_token()
        else:
            return Token(Lexem.HTML, content)

    def _get_template_token(self):
        if self._is_comment:
            self._is_comment = False
            return self._get_comment()

        content = self._get_next_char()
        if content.isdigit():
            return self._get_number_token(content)
        elif content == "'" or content == '"':
            return self._get_string_token(content)
        elif content.isalpha():
            return self._get_keyword_or_identifier_token(content)
        elif content in symbols and content not in ['%', '=', '<', '>']:
            return Token(symbols[content])

        content += self._get_next_char()
        if content in symbols:
            if symbols[content] == Lexem.COMMENT_OPEN:
                self._is_comment = True
            elif symbols[content] == self._template_end_token_id:
                self._is_template = False
                self._template_end_token_id = None
            return Token(symbols[content])
        elif content[0] in ['%', '=', '<', '>']:
            self._read_source = content[1:] + self._read_source
            return Token(symbols[content[0]])
        else:
            raise ParserSyntaxError('Unrecognised construction: {}'.format(content[0]),
                                    self._source_controller.line_number,
                                    self._source_controller.position_number - len(self._read_source) - 1)

    def _get_number_token(self, first_digit):
        number = first_digit
        while not self.is_end() and is_number(number):
            number += self._get_next_char()

        if not is_number(number):
            self._read_source = number[-1:] + self._read_source
            number = number[:-1]
        if '.' in number:
            return Token(Lexem.NUMBER, float(number))
        else:
            return Token(Lexem.INT, int(number))

    def _get_string_token(self, quotation):
        char = self._get_next_char()
        string = quotation + char
        while not self.is_end() and char != quotation:
            char = self._get_next_char()
            string += char
        if char == quotation:
            return Token(Lexem.STRING, string)
        else:
            raise ParserSyntaxError('Unclosed string',
                                    self._source_controller.line_number,
                                    self._source_controller.position_number - len(self._read_source))

    def _get_keyword_or_identifier_token(self, quotation):
        char = self._get_next_char()
        string = quotation
        while not self.is_end() and (char.isdigit() or char.isalpha()):
            string += char
            char = self._get_next_char()
        if char.isdigit() or char.isalpha():
            string += char
        else:
            self._read_source = char + self._read_source

        if string in keywords:
            return Token(keywords[string])
        else:
            return Token(Lexem.IDENTIFIER, string)

    def _get_comment(self):
        comment = ''
        while not self.is_end() and comment[-2:] != '#}':
            comment += self._get_next_char()
        if comment[-2:] == '#}':
            self._read_source = comment[-2:] + self._read_source
            self._is_comment = False
            return Token(Lexem.COMMENT, comment[:-2])
        else:
            return Token(Lexem.COMMENT, comment)

    def _is_template_opener_in(self, source):
        return source[-2:] in ['{%', '{{', '{#']


class SourceController:
    """Class reads from input stream and place characters in buffer.
    Stores information about line and position."""

    def __init__(self, input_stream):
        self.line_number = 0
        self.position_number = 0
        self.buffer = ''
        self._input = input_stream

    def get_char(self):
        """Returns character from source and None if end of file."""
        if not self.has_char():
            return ''
        result = self.buffer[self.position_number]
        self.position_number += 1
        return result

    def has_char(self):
        """Returns True whether there is text to read."""
        return bool(not self._is_empty_buffer() or self._next_line())

    def _next_line(self):
        """Reads next line and place it in buffer. Returns the buffer."""
        self.buffer = self._input.readline()
        if self.buffer:
            self.line_number += 1
            self.position_number = 0
        return self.buffer

    def _is_empty_buffer(self):
        return not self.position_number < len(self.buffer)
