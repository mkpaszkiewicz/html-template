__all__ = [
    'ParserError',
    'ParserSyntaxError',
    'ParserSemanticError',
    'ParserArgumentError'
]


class ParserError(Exception):
    """Base class for all parser exceptions."""

    def __init__(self, msg, position=None):
        if position:
            pos = '{}:{}: '.format(position[0], position[1])
        else:
            pos = ''
        self.message = '{}error: {}'.format(pos, msg)
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class ParserSyntaxError(ParserError):
    """Raised when forbidden symbols are met or
    token is incomplete e.g. unclosed string"""

    def __init__(self, msg, line, position):
        ParserError.__init__(self, msg, (line, position))


class ParserSemanticError(ParserError):
    """Raised when dividing by 0"""

    def __init__(self, msg):
        ParserError.__init__(self, msg)


class ParserArgumentError(ParserError):
    """Raised when got invalid argument"""

    def __init__(self, msg):
        ParserError.__init__(self, msg)
