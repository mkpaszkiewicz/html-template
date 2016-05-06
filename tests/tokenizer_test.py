import io
import itertools
import unittest
from contextlib import closing

from html_template_parser import SourceController, Tokenizer, Lexem, Token


class SourceControllerTest(unittest.TestCase):
    """SourceController class test cases"""
    FILE_CONTENT = 'exemplary content\nsecond line\n'

    def setUp(self):
        self.input_stream = io.StringIO(self.FILE_CONTENT)
        self.source_controller = SourceController(self.input_stream)

    def tearDown(self):
        self.input_stream.close()

    def test_buffer_should_be_empty_before_first_get_char(self):
        self.assertTrue(self.source_controller._is_empty_buffer(), 'Buffer instead of being empty contains ' +
                        self.source_controller.buffer)
        self.assertEqual(self.source_controller.buffer, '')

    def test_should_return_file_content(self):
        i = 0
        while self.source_controller.has_char():
            char = self.source_controller.get_char()
            self.assertEqual(char, self.FILE_CONTENT[i])
            i += 1

    def test_should_update_position(self):
        i = 0
        line_number = 1
        position_number = 1
        while self.source_controller.has_char():
            char = self.source_controller.get_char()
            msg = 'Got ' + char + ' instead of ' + self.FILE_CONTENT[i] + \
                  ' on line: ' + str(line_number) + ' pos: ' + str(position_number)
            self.assertEqual(self.source_controller.line_number, line_number, msg)
            self.assertEqual(self.source_controller.position_number, position_number, msg)
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
            tokenizer = Tokenizer(SourceController(input_stream))
            token = tokenizer.get_next_token()
            self.assertEqual(token.id, Lexem.EOI)
            token = tokenizer.get_next_token()
            self.assertEqual(token.id, Lexem.EOI)

    def test_should_return_single_html_token(self):
        with closing(io.StringIO('<span>Hello World</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>Hello World</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_template_token(self):
        with closing(io.StringIO('{%%}')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.TEMPLATE_OPEN), Token(Lexem.TEMPLATE_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_statement_token(self):
        with closing(io.StringIO('{{}}')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.STATEMENT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_plus_token(self):
        with closing(io.StringIO('{{+')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.PLUS)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_minus_token(self):
        with closing(io.StringIO('{{-')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.MINUS)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_div_token(self):
        with closing(io.StringIO('{{/')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.SLASH)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_mod_token(self):
        with closing(io.StringIO('{{%')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.MOD)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_mul_token(self):
        with closing(io.StringIO('{{*')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.STAR)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_keyword_token(self):
        with closing(io.StringIO('{%macro')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.TEMPLATE_OPEN), Token(Lexem.MACRO)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_identifier_token(self):
        with closing(io.StringIO('{%identifier')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.TEMPLATE_OPEN), Token(Lexem.IDENTIFIER, 'identifier')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_assign_token(self):
        with closing(io.StringIO('{{=')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.ASSIGN)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_lower_than_token(self):
        with closing(io.StringIO('{{<')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.LT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_greater_than_token(self):
        with closing(io.StringIO('{{>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.GT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_lower_or_equal_token(self):
        with closing(io.StringIO('{{<=')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.LE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_greater_or_equal_token(self):
        with closing(io.StringIO('{{>=')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.GE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_equal_token(self):
        with closing(io.StringIO('{{==')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.EQ)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_not_equal_token(self):
        with closing(io.StringIO('{{!=')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.NEQ)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_comma_token(self):
        with closing(io.StringIO('{{,')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.COMMA)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_dot_token(self):
        with closing(io.StringIO('{{.')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.DOT)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_left_bracket_token(self):
        with closing(io.StringIO('{{(')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.LEFT_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_right_bracket_token(self):
        with closing(io.StringIO('{{)')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.RIGHT_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_left_square_bracket_token(self):
        with closing(io.StringIO('{{[')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.LEFT_SQUARE_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_right_square_bracket_token(self):
        with closing(io.StringIO('{{]')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.STATEMENT_OPEN), Token(Lexem.RIGHT_SQUARE_BRACKET)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_comment_token(self):
        with closing(io.StringIO('{##}')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.COMMENT_OPEN), Token(Lexem.COMMENT, ''), Token(Lexem.COMMENT_CLOSE)]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_statement_tokens(self):
        with closing(io.StringIO('<span>{{}}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.STATEMENT_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_string_tokens(self):
        with closing(io.StringIO('<span>{{\'str1{{1+2}}b\'"str2\'/{#%"""\'\'}}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.STRING, '\'str1{{1+2}}b\''),
                      Token(Lexem.STRING, '"str2\'/{#%"'), Token(Lexem.STRING, '""'), Token(Lexem.STRING, '\'\''),
                      Token(Lexem.STATEMENT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_error_unclosed_string(self):
        with closing(io.StringIO('<span>{{"}}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.ERROR, 'Unclosed string')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_number_tokens(self):
        with closing(io.StringIO('<span>{{123}}{{12.3}}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN), Token(Lexem.NUMBER, 123),
                      Token(Lexem.STATEMENT_CLOSE), Token(Lexem.STATEMENT_OPEN),
                      Token(Lexem.NUMBER, 12.3), Token(Lexem.STATEMENT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_comment_tokens(self):
        with closing(io.StringIO('<span>{#Comment {{12.3}}#}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.COMMENT_OPEN), Token(Lexem.COMMENT, 'Comment {{12.3}}'),
                      Token(Lexem.COMMENT_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_whitespace_tokens(self):
        with closing(io.StringIO('<span>{% \n %}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN), Token(Lexem.SPACE),
                      Token(Lexem.NEW_LINE), Token(Lexem.SPACE), Token(Lexem.TEMPLATE_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_keyword_and_identifier_tokens(self):
        with closing(io.StringIO('<span>{% if condition %}Hello World{% endif %}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN), Token(Lexem.SPACE),
                      Token(Lexem.IF), Token(Lexem.SPACE), Token(Lexem.IDENTIFIER, 'condition'),
                      Token(Lexem.SPACE), Token(Lexem.TEMPLATE_CLOSE), Token(Lexem.HTML, 'Hello World'),
                      Token(Lexem.TEMPLATE_OPEN), Token(Lexem.SPACE), Token(Lexem.ENDIF),
                      Token(Lexem.SPACE), Token(Lexem.TEMPLATE_CLOSE), Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def test_should_return_expression_tokens(self):
        with closing(io.StringIO('<span>{% set var = (2+4%3) %}</span>')) as input_stream:
            tokenizer = Tokenizer(SourceController(input_stream))
            tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN), Token(Lexem.SPACE),
                      Token(Lexem.SET), Token(Lexem.SPACE), Token(Lexem.IDENTIFIER, 'var'),
                      Token(Lexem.SPACE), Token(Lexem.ASSIGN), Token(Lexem.SPACE),
                      Token(Lexem.LEFT_BRACKET), Token(Lexem.NUMBER, 2), Token(Lexem.PLUS),
                      Token(Lexem.NUMBER, 4), Token(Lexem.MOD), Token(Lexem.NUMBER, 3),
                      Token(Lexem.RIGHT_BRACKET), Token(Lexem.SPACE), Token(Lexem.TEMPLATE_CLOSE),
                      Token(Lexem.HTML, '</span>')]
            self.assertTokenListEqual(tokens, list(tokenizer.get_tokens()))

    def assertTokenListEqual(self, tokens1, tokens2):
        for expected, generated in itertools.zip_longest(tokens1, tokens2):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)


if __name__ == '__main__':
    unittest.main()
