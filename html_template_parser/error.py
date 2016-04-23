__all__ = [
    'ParserException'
]


class ParserException(Exception):
    """Base class for all parser exceptions."""

    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__
