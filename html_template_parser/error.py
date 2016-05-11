__all__ = [
    'ParserException',
    'UnrecognisedConstruction',
    'IncompleteToken'
]


class ParserException(Exception):
    """Base class for all parser exceptions."""

    def __init__(self, msg, line, position):
        self.message = '{}:{}: error: {}'.format(line, position, msg)
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class UnrecognisedConstruction(ParserException):
    """Raised when forbidden symbols are met."""

    def __init__(self, line, position, error_msg):
        ParserException.__init__(self, line, position, error_msg)


class IncompleteToken(ParserException):
    """Raised when any token is incomplete e.g. unclosed string"""

    def __init__(self, line, position, error_msg):
        ParserException.__init__(self, line, position, error_msg)
