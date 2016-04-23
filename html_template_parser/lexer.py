from html_template_parser.token import Token

tokens = {
    'macro': Token.Token.MACRO,
    'endmacro': Token.Token.ENDMACRO,
    'set': Token.SET,
    'if': Token.IF,
    'elif': Token.ELIF,
    'else': Token.ELSE,
    'endif': Token.ENDIF,
    'for': Token.FOR,
    'endfor': Token.ENDFOR,
    'in': Token.IN,

    'and': Token.AND,
    'or': Token.OR,
    'not': Token.NOT,

    '+': Token.PLUS,
    '-': Token.MINUS,
    '/': Token.SLASH,
    '%': Token.MOD,
    '*': Token.STAR,

    '=': Token.ASSIGN,
    '<': Token.LT,
    '>': Token.GT,
    '<=': Token.LE,
    '>=': Token.GE,
    '==': Token.EQ,
    '!=': Token.NEQ,

    ',': Token.COMMA,
    '.': Token.DOT,
    '(': Token.LEFT_BRACKET,
    ')': Token.RIGHT_BRACKET,
    '[': Token.LEFT_SQUARE_BRACKET,
    ']': Token.RIGHT_SQUARE_BRACKET,

    '{%': Token.TEMPLATE_OPEN,
    '}%': Token.TEMPLATE_CLOSE,
    '{{': Token.STATEMENT_OPEN,
    '}}': Token.STATEMENT_CLOSE,
    '{#': Token.COMMENT_OPEN,
    '#}': Token.COMMENT_CLOSE,

    ' ': Token.WHITESPACE,
    '\n': Token.Token.WHITESPACE,
    '\t': Token.Token.WHITESPACE
}


class SourceController:
    """Class reads from input stream and place characters in buffer.
    Stores information about line and position."""

    def __init__(self, source):
        self.line_number = 0
        self.position_number = 0
        self.buffer = ''
        self._source = source

    def __enter__(self):
        self._input = open(self._source, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._input.close()

    def get_char(self):
        """Returns character from source and None if end of file"""
        if self._is_empty_buffer() and not self._next_line():
            return None
        result = self.buffer[self.position_number]
        self.position_number += 1
        return result

    def _next_line(self):
        """Reads next line and place it in buffer. Returns the buffer."""
        self.buffer = self._input.readline()
        self.line_number += 1
        self.position_number = 0
        return self.buffer

    def _is_empty_buffer(self):
        return not self.position_number < len(self.buffer)
