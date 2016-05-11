__all__ = [
    'TokenizerException',
    'UnrecognisedConstruction',
    'IncompleteToken'
]


class TokenizerException(Exception):
    """Base class for all tokenizer exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__


class UnrecognisedConstruction(TokenizerException):
    """Raised when forbidden symbols are met."""

    def __init__(self, line, position, error_msg):
        msg = '{}:{}: error: {}'.format(line, position, error_msg)
        TokenizerException.__init__(self, msg)


class IncompleteToken(TokenizerException):
    """Raised when any token is incomplete e.g. unclosed string"""

    def __init__(self, line, position, error_msg):
        msg = '{}:{}: error: {}'.format(line, position, error_msg)
        TokenizerException.__init__(self, msg)
