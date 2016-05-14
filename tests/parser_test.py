import io
import unittest
from contextlib import closing

from html_template_parser.error import *
from html_template_parser.parser import parse


class ParserTest(unittest.TestCase):
    """Parser test cases"""
    CSV_FILE = '~parser_test_model.csv'

    @classmethod
    def setUpClass(cls):
        with open(cls.CSV_FILE, 'w+') as f:
            f.write('firstname,lastname,salary,age\n'
                     'Brad,Smith,2500.00,34\n'
                     'Will,Pitt,3000.00,42\n'
                     'Jennifer,Polez,100.00,17\n')

    @classmethod
    def tearDownClass(cls):
        import os
        os.remove(cls.CSV_FILE)

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
        with closing(io.StringIO('{{17 / 3')) as input_stream:
            self.assertRaises(ParserSyntaxError, parse, input_stream)

    def test_should_print_string(self):
        with closing(io.StringIO('{{ "Hello world" }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('Hello world', output)

    def test_should_concatenate_strings(self):
        with closing(io.StringIO('{{ "Hello " + "world" }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('Hello world', output)

    def test_should_accept_both_string_quatation(self):
        with closing(io.StringIO('{{ "Hello " + \'world\' }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('Hello world', output)

    def test_should_print_boolean_true(self):
        with closing(io.StringIO('{{ True }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_print_boolean_false(self):
        with closing(io.StringIO('{{ False }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('False', output)

    def test_should_add_booleans(self):
        with closing(io.StringIO('{{ True + False }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('1', output)

    def test_should_multiply_booleans(self):
        with closing(io.StringIO('{{ 4 * True }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('4', output)

    def test_should_conjunct_boolean_expression(self):
        with closing(io.StringIO('{{ True and False }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('False', output)

    def test_should_alternate_boolean_expression(self):
        with closing(io.StringIO('{{ True or False }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_conjunct_complex_boolean_expression1(self):
        with closing(io.StringIO('{{ not True and False or not False and True}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_conjunct_complex_boolean_expression2(self):
        with closing(io.StringIO('{{ 2 and (False or not False) and True}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_return_string_from_boolean_expression(self):
        with closing(io.StringIO('{{ False or "str"}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('str', output)

    def test_should_check_if_char_is_in_string(self):
        with closing(io.StringIO('{{ "t" in "str"}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_check_if_char_is_not_in_string(self):
        with closing(io.StringIO('{{ not "a" in "str"}}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_raise_semantic_error(self):
        with closing(io.StringIO('{{ True in "str" }}')) as input_stream:
            self.assertRaises(ParserSemanticError, parse, input_stream)

    def test_should_compare_integers1(self):
        with closing(io.StringIO('{{ 5 > 3 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_compare_integers2(self):
        with closing(io.StringIO('{{ 5 < 3 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('False', output)

    def test_should_compare_integers3(self):
        with closing(io.StringIO('{{ 2 == 2 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_compare_integers4(self):
        with closing(io.StringIO('{{ 2 != 2 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('False', output)

    def test_should_compare_arithmetic_results(self):
        with closing(io.StringIO('{{ 2 * 3 >= 6 and 2 < 6 }}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('True', output)

    def test_should_print_results_from_if_statement(self):
        with closing(io.StringIO('{% if True %}Hello World{% endif %}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('Hello World', output)

    def test_should_not_print_results_from_if_statement(self):
        with closing(io.StringIO('{% if 5 < 3 %}Hello World{% endif %}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('', output)

    def test_should_print_results_from_else_statement(self):
        with closing(io.StringIO('{% if False %}Hello{% else %}World{% endif %}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('World', output)

    def test_should_print_results_from_elif_statement(self):
        with closing(io.StringIO('{% if False %}Hello{% elif True %}World{% endif %}')) as input_stream:
            output = parse(input_stream)
            self.assertEqual('World', output)

    def test_should_get_value_from_csv_file(self):
        with closing(io.StringIO("{{ csv[0]['age'] }}")) as input_stream:
            output = parse(input_stream, self.CSV_FILE)
            self.assertEqual('34', output)

    def test_should_add_values_from_csv_file(self):
        with closing(io.StringIO("{{ csv[0]['age'] + csv[1]['age'] }}")) as input_stream:
            output = parse(input_stream, self.CSV_FILE)
            self.assertEqual('76', output)

    def test_should_concatenate_values_from_csv_file(self):
        with closing(io.StringIO("{{ csv[0]['firstname'] + ' ' + csv[0]['lastname'] }}")) as input_stream:
            output = parse(input_stream, self.CSV_FILE)
            self.assertEqual('Brad Smith', output)

    def test_should_raise_exception_unknown_key(self):
        with closing(io.StringIO("{{ csv[0]['date_of_birth'] }}")) as input_stream:
            self.assertRaises(ParserSemanticError, parse, input_stream, self.CSV_FILE)

    def test_should_accept_inverted_indexing(self):
        with closing(io.StringIO("{{ csv[-1]['age'] }}")) as input_stream:
            output = parse(input_stream, self.CSV_FILE)
            self.assertEqual('17', output)

    if __name__ == '__main__':
        unittest.main()
