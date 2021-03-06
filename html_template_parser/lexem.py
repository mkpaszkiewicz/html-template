import enum


class Lexem(enum.IntEnum):
    EOI = 0

    INT = 1
    NUMBER = 2
    STRING = 3
    IDENTIFIER = 4

    MACRO = 5
    ENDMACRO = 6
    SET = 7
    IF = 8
    ELIF = 9
    ELSE = 10
    ENDIF = 11
    FOR = 12
    ENDFOR = 13
    IN = 14

    AND = 15
    OR = 16
    NOT = 17

    PLUS = 18
    MINUS = 19
    SLASH = 20
    MOD = 21
    STAR = 22

    ASSIGN = 23
    LT = 24
    GT = 25
    LE = 26
    GE = 27
    EQ = 28
    NEQ = 29

    COMMA = 30
    DOT = 31
    LEFT_BRACKET = 32
    RIGHT_BRACKET = 33
    LEFT_SQUARE_BRACKET = 34
    RIGHT_SQUARE_BRACKET = 35

    STATEMENT_OPEN = 36
    STATEMENT_CLOSE = 37
    PRINT_OPEN = 38
    PRINT_CLOSE = 39
    COMMENT_OPEN = 40
    COMMENT_CLOSE = 41

    HTML = 42

    TRUE = 43
    FALSE = 44


keywords = {
    'macro': Lexem.MACRO,
    'endmacro': Lexem.ENDMACRO,
    'set': Lexem.SET,
    'if': Lexem.IF,
    'elif': Lexem.ELIF,
    'else': Lexem.ELSE,
    'endif': Lexem.ENDIF,
    'for': Lexem.FOR,
    'endfor': Lexem.ENDFOR,
    'in': Lexem.IN,

    'and': Lexem.AND,
    'or': Lexem.OR,
    'not': Lexem.NOT,

    'True': Lexem.TRUE,
    'False': Lexem.FALSE
}

reverted_keywords = dict(zip(keywords.values(), keywords.keys()))

symbols = {
    '+': Lexem.PLUS,
    '-': Lexem.MINUS,
    '/': Lexem.SLASH,
    '%': Lexem.MOD,
    '*': Lexem.STAR,

    '=': Lexem.ASSIGN,
    '<': Lexem.LT,
    '>': Lexem.GT,
    '<=': Lexem.LE,
    '>=': Lexem.GE,
    '==': Lexem.EQ,
    '!=': Lexem.NEQ,

    ',': Lexem.COMMA,
    '.': Lexem.DOT,
    '(': Lexem.LEFT_BRACKET,
    ')': Lexem.RIGHT_BRACKET,
    '[': Lexem.LEFT_SQUARE_BRACKET,
    ']': Lexem.RIGHT_SQUARE_BRACKET,

    '{%': Lexem.STATEMENT_OPEN,
    '%}': Lexem.STATEMENT_CLOSE,
    '{{': Lexem.PRINT_OPEN,
    '}}': Lexem.PRINT_CLOSE,
    '{#': Lexem.COMMENT_OPEN,
    '#}': Lexem.COMMENT_CLOSE,
}

reverted_symbols = dict(zip(symbols.values(), symbols.keys()))
