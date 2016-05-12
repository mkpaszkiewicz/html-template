import io
import unittest
from contextlib import closing

from html_template_parser.parser import parse
from html_template_parser.error import *


class ParserTest(unittest.TestCase):
    """Parser test cases"""

    def test_should_generate_empty_string(self):
        with closing(io.StringIO('')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('', output)

    def test_should_generate_simple_html(self):
        with closing(io.StringIO('<span>Hello World</span>')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('<span>Hello World</span>', output)

    def test_should_omit_comment(self):
        with closing(io.StringIO('{# comment #}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('', output)

    def test_should_delete_comment_from_simple_html(self):
        with closing(io.StringIO('<span>Hello {# comment #}World</span>')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('<span>Hello World</span>', output)

    def test_should_add_numbers(self):
        with closing(io.StringIO('{{ 2 + 3 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('5', output)

    def test_should_add_numbers_and_convert_to_float(self):
        with closing(io.StringIO('{{ 2 + 3.0 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('5.0', output)

    def test_should_subtract_numbers(self):
        with closing(io.StringIO('{{ 2 - 3 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('-1', output)

    def test_should_subtract_numbers_and_convert_to_float(self):
        with closing(io.StringIO('{{ 2 - 3.0 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('-1.0', output)

    def test_should_multiply_numbers(self):
        with closing(io.StringIO('{{ 2 * 3 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('6', output)

    def test_should_multiply_numbers_and_convert_to_float(self):
        with closing(io.StringIO('{{ 2 * -3.0 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('-6.0', output)

    def test_should_divide_numbers(self):
        with closing(io.StringIO('{{ 8 / 2 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('4.0', output)

    def test_should_calculate_modulo(self):
        with closing(io.StringIO('{{7 % 3}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('1', output)

    def test_should_calculate_result_in_brackets(self):
        with closing(io.StringIO('{{ ((8 / 2) + (2) * 3) + 7 % 3}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('11.0', output)

    def test_should_raise_division_by_zero_error1(self):
        with closing(io.StringIO('{{7 % 0}}')) as input_stream:
            self.assertRaises(ParserSemanticError, parse, input_stream)

    def test_should_raise_division_by_zero_error2(self):
        with closing(io.StringIO('{{17 / 0}}')) as input_stream:
            self.assertRaises(ParserSemanticError, parse, input_stream)

    def test_should_raise_syntax_error(self):
        with closing(io.StringIO('{{17 / 0')) as input_stream:
            self.assertRaises(ParserSyntaxError, parse, input_stream)

if __name__ == '__main__':
    unittest.main()
