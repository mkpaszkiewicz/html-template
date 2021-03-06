import io
import itertools
import unittest
from contextlib import closing

from html_template_parser.error import *
from html_template_parser.lexem import *
from html_template_parser.tokenizer import Tokenizer, Token, SourceController


class SourceControllerTest(unittest.TestCase):
    """SourceController class test cases"""
    FILE_CONTENT = 'exemplary content\nsecond line\n'

    def setUp(self):
        self.input_stream = io.StringIO(self.FILE_CONTENT)

    def tearDown(self):
        self.input_stream.close()

    def test_buffer_should_be_empty_before_first_get_char(self):
        source_controller = SourceController(self.input_stream)
        self.assertTrue(source_controller._is_empty_buffer(), 'Buffer instead of being empty contains ' +
                        source_controller.buffer)
        self.assertEqual(source_controller.buffer, '')

    def test_should_return_file_content(self):
        source_controller = SourceController(self.input_stream)
        i = 0
        while source_controller.has_char():
            char = source_controller.get_char()
            self.assertEqual(char, self.FILE_CONTENT[i])
            i += 1

    def test_should_update_position(self):
        tokenizer = Tokenizer(self.input_stream)
        i = 0
        line_number = 1
        position_number = 1
        while tokenizer._source_controller.has_char():
            char = tokenizer._source_controller.get_char()
            msg = 'Got ' + char + ' instead of ' + self.FILE_CONTENT[i] + \
                  ' on line: ' + str(line_number) + ' pos: ' + str(position_number)
            self.assertEqual(tokenizer._source_controller.line_number, line_number, msg)
            self.assertEqual(tokenizer._source_controller.position_number, position_number, msg)
            if self.FILE_CONTENT[i] == '\n':
                line_number += 1
                position_number = 1
            else:
                position_number += 1
            i += 1


class TokenizerTest(unittest.TestCase):
    """Tokenizer class test cases"""

    def test_should_return_eoi(self):
        with closing(io.StringIO('')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            token = tokenizer.get_next_token()
            self.assertEqual(token.id, Lexem.EOI)
            token = tokenizer.get_next_token()
            self.assertEqual(token.id, Lexem.EOI)

    def test_should_return_single_html_token(self):
        with closing(io.StringIO('<span>Hello World</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>Hello World</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_template_token(self):
        with closing(io.StringIO('{%%}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.STATEMENT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_statement_token(self):
        with closing(io.StringIO('{{}}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.PRINT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_plus_token(self):
        with closing(io.StringIO('{{+')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.PLUS)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_minus_token(self):
        with closing(io.StringIO('{{-')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.MINUS)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_div_token(self):
        with closing(io.StringIO('{{/')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.SLASH)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_mod_token(self):
        with closing(io.StringIO('{{%')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.MOD)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_mul_token(self):
        with closing(io.StringIO('{{*')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.STAR)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_keyword_token(self):
        with closing(io.StringIO('{%macro')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.MACRO)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_identifier_token(self):
        with closing(io.StringIO('{%identifier')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.IDENTIFIER, 'identifier')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_assign_token(self):
        with closing(io.StringIO('{{=')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.ASSIGN)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_lower_than_token(self):
        with closing(io.StringIO('{{<')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.LT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_greater_than_token(self):
        with closing(io.StringIO('{{>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.GT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_lower_or_equal_token(self):
        with closing(io.StringIO('{{<=')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.LE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_greater_or_equal_token(self):
        with closing(io.StringIO('{{>=')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.GE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_equal_token(self):
        with closing(io.StringIO('{{==')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.EQ)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_not_equal_token(self):
        with closing(io.StringIO('{{!=')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.NEQ)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_comma_token(self):
        with closing(io.StringIO('{{,')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.COMMA)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_dot_token(self):
        with closing(io.StringIO('{{.')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.DOT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_left_bracket_token(self):
        with closing(io.StringIO('{{(')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.LEFT_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_right_bracket_token(self):
        with closing(io.StringIO('{{)')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.RIGHT_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_left_square_bracket_token(self):
        with closing(io.StringIO('{{[')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.LEFT_SQUARE_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_right_square_bracket_token(self):
        with closing(io.StringIO('{{]')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.RIGHT_SQUARE_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_omit_comment(self):
        with closing(io.StringIO('{##}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = []
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_statement_tokens(self):
        with closing(io.StringIO('<span>{{}}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.PRINT_OPEN), Token(Lexem.PRINT_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_string_token(self):
        with closing(io.StringIO('{{"Hello World"}}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.STRING, 'Hello World'), Token(Lexem.PRINT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_string_tokens(self):
        with closing(io.StringIO('<span>{{\'str1{{1+2}}b\'"str2\'/{#%"""\'\'}}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.PRINT_OPEN), Token(Lexem.STRING, 'str1{{1+2}}b'),
                      Token(Lexem.STRING, 'str2\'/{#%'), Token(Lexem.STRING, ''), Token(Lexem.STRING, ''),
                      Token(Lexem.PRINT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_raise_incomplete_token_exception(self):
        with closing(io.StringIO('<span>{{"}}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            self.assertEqual(Token(Lexem.HTML, '<span>'), tokenizer.get_next_token())
            self.assertEqual(Token(Lexem.PRINT_OPEN), tokenizer.get_next_token())
            self.assertRaises(ParserSyntaxError, tokenizer.get_next_token)

    def test_should_return_raise_incomplete_unrecognised_construction(self):
        with closing(io.StringIO('<span>{{^2 + 1}}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            self.assertEqual(Token(Lexem.HTML, '<span>'), tokenizer.get_next_token())
            self.assertEqual(Token(Lexem.PRINT_OPEN), tokenizer.get_next_token())
            self.assertRaises(ParserSyntaxError, tokenizer.get_next_token)

    def test_should_return_number_tokens(self):
        with closing(io.StringIO('<span>{{123}}{{12.3}}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.PRINT_OPEN), Token(Lexem.INT, 123),
                      Token(Lexem.PRINT_CLOSE), Token(Lexem.PRINT_OPEN),
                      Token(Lexem.NUMBER, 12.3), Token(Lexem.PRINT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_omit_commented_text(self):
        with closing(io.StringIO('<span>{#Comment {{12.3}}#}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_omit_whitespaces(self):
        with closing(io.StringIO('<span>{% \n %}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.STATEMENT_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_keyword_and_identifier_tokens(self):
        with closing(io.StringIO('<span>{% if condition %}Hello World{% endif %}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.IF),
                      Token(Lexem.IDENTIFIER, 'condition'), Token(Lexem.STATEMENT_CLOSE), Token(Lexem.HTML, 'Hello World'),
                      Token(Lexem.STATEMENT_OPEN), Token(Lexem.ENDIF), Token(Lexem.STATEMENT_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_expression_tokens(self):
        with closing(io.StringIO('<span>{% set var = (2+4%3.0) %}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.SET),
                      Token(Lexem.IDENTIFIER, 'var'), Token(Lexem.ASSIGN), Token(Lexem.LEFT_BRACKET),
                      Token(Lexem.INT, 2), Token(Lexem.PLUS), Token(Lexem.INT, 4), Token(Lexem.MOD),
                      Token(Lexem.NUMBER, 3), Token(Lexem.RIGHT_BRACKET), Token(Lexem.STATEMENT_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_token_list_without_whitespaces(self):
        with closing(io.StringIO('<span>{% if condition %}Hello World{% endif %}</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN),
                      Token(Lexem.IF), Token(Lexem.IDENTIFIER, 'condition'),
                      Token(Lexem.STATEMENT_CLOSE), Token(Lexem.HTML, 'Hello World'),
                      Token(Lexem.STATEMENT_OPEN), Token(Lexem.ENDIF),
                      Token(Lexem.STATEMENT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_boolean_true(self):
        with closing(io.StringIO('{{ True }}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.TRUE), Token(Lexem.PRINT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_boolean_false(self):
        with closing(io.StringIO('{{ False }}')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tokens = [Token(Lexem.PRINT_OPEN), Token(Lexem.FALSE), Token(Lexem.PRINT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def assertTokenListEqual(self, tokens1, tokens2):
        for expected, generated in itertools.zip_longest(tokens1, tokens2):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)


if __name__ == '__main__':
    unittest.main()
