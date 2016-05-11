import io
import unittest
import itertools
from contextlib import closing

from html_template_parser.parser import parse


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

    def assertParserTree(self, tokens, nodes):
        for expected, generated_node in itertools.zip_longest(tokens, nodes):
            self.assertEqual(expected.id, generated_node.data.id)
            self.assertEqual(expected.content, generated_node.data.content)

if __name__ == '__main__':
    unittest.main()
