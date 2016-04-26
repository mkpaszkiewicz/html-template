import io
import itertools
import unittest

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
        input_stream = io.StringIO('')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)

        token = tokenizer.get_next_token()
        self.assertEqual(token.id, Lexem.EOI)
        token = tokenizer.get_next_token()
        self.assertEqual(token.id, Lexem.EOI)
        input_stream.close()

    def test_should_return_single_html_token(self):
        input_stream = io.StringIO('<span>Hello World</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>Hello World</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_statement_tokens(self):
        input_stream = io.StringIO('<span>{{}}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN, '{{'), Token(Lexem.STATEMENT_CLOSE, '}}'),
                  Token(Lexem.HTML, '</span>')]

        # generated = list(tokenizer.get_tokens()
        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_string_tokens(self):
        input_stream = io.StringIO('<span>{{\'str1{{1+2}}b\'"str2\'/{#%"""\'\'}}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN, '{{'), Token(Lexem.STRING, '\'str1{{1+2}}b\''),
                  Token(Lexem.STRING, '"str2\'/{#%"'), Token(Lexem.STRING, '""'), Token(Lexem.STRING, '\'\''),
                  Token(Lexem.STATEMENT_CLOSE, '}}'), Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_error_unclosed_string(self):
        input_stream = io.StringIO('<span>{{"}}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN, '{{'), Token(Lexem.ERROR, 'Unclosed string')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_number_tokens(self):
        input_stream = io.StringIO('<span>{{123}}{{12.3}}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.STATEMENT_OPEN, '{{'), Token(Lexem.NUMBER, '123'),
                  Token(Lexem.STATEMENT_CLOSE, '}}'), Token(Lexem.HTML, ''), Token(Lexem.STATEMENT_OPEN, '{{'),
                  Token(Lexem.NUMBER, '12.3'), Token(Lexem.STATEMENT_CLOSE, '}}'), Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_comment_tokens(self):
        input_stream = io.StringIO('<span>{#Comment {{12.3}}#}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.COMMENT_OPEN, '{#'), Token(Lexem.COMMENT, 'Comment {{12.3}}'),
                  Token(Lexem.COMMENT_CLOSE, '#}'), Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_whitespace_tokens(self):
        input_stream = io.StringIO('<span>{% \n %}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN, '{%'), Token(Lexem.WHITESPACE, ' '),
                  Token(Lexem.WHITESPACE, '\n'), Token(Lexem.WHITESPACE, ' '), Token(Lexem.TEMPLATE_CLOSE, '%}'),
                  Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_keyword_and_identifier_tokens(self):
        input_stream = io.StringIO('<span>{% if condition %}Hello World{% endif %}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN, '{%'), Token(Lexem.WHITESPACE, ' '),
                  Token(Lexem.IF, 'if'), Token(Lexem.WHITESPACE, ' '), Token(Lexem.IDENTIFIER, 'condition'),
                  Token(Lexem.WHITESPACE, ' '), Token(Lexem.TEMPLATE_CLOSE, '%}'), Token(Lexem.HTML, 'Hello World'),
                  Token(Lexem.TEMPLATE_OPEN, '{%'), Token(Lexem.WHITESPACE, ' '), Token(Lexem.ENDIF, 'endif'),
                  Token(Lexem.WHITESPACE, ' '), Token(Lexem.TEMPLATE_CLOSE, '%}'), Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

    def test_should_return_expression_tokens(self):
        input_stream = io.StringIO('<span>{% set var = (2+4%3) %}</span>')
        source_controller = SourceController(input_stream)
        tokenizer = Tokenizer(source_controller)
        tokens = [Token(Lexem.HTML, '<span>'), Token(Lexem.TEMPLATE_OPEN, '{%'), Token(Lexem.WHITESPACE, ' '),
                  Token(Lexem.SET, 'set'), Token(Lexem.WHITESPACE, ' '), Token(Lexem.IDENTIFIER, 'var'),
                  Token(Lexem.WHITESPACE, ' '), Token(Lexem.ASSIGN, '='), Token(Lexem.WHITESPACE, ' '),
                  Token(Lexem.LEFT_BRACKET, '('), Token(Lexem.NUMBER, '2'), Token(Lexem.PLUS, '+'),
                  Token(Lexem.NUMBER, '4'), Token(Lexem.MOD, '%'), Token(Lexem.NUMBER, '3'),
                  Token(Lexem.RIGHT_BRACKET, ')'), Token(Lexem.WHITESPACE, ' '), Token(Lexem.TEMPLATE_CLOSE, '%}'),
                  Token(Lexem.HTML, '</span>')]

        for expected, generated in itertools.zip_longest(tokens, list(tokenizer.get_tokens())):
            self.assertEqual(expected.id, generated.id)
            self.assertEqual(expected.content, generated.content)
        input_stream.close()

if __name__ == '__main__':
    unittest.main()
