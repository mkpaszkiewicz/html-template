import io
import unittest
import itertools
from contextlib import closing

from treelib import Node

from html_template_parser import Tokenizer, Token, Lexem
from html_template_parser.parser import generate_tree


class ParserTreeGenerationTest(unittest.TestCase):
    """Parser tree generation test cases"""

    def test_should_return_token_list_without_whitespaces(self):
        with closing(io.StringIO('<span>Hello World</span>')) as input_stream:
            tokenizer = Tokenizer(input_stream)
            tree = generate_tree(tokenizer.get_tokens(omit_whitespace=True))

            self.assertParserTree([Token(Lexem.HTML, '<span>Hello World</span>')], tree.all_nodes())

    def assertParserTree(self, tokens, nodes):
        for expected, generated_node in itertools.zip_longest(tokens, nodes):
            self.assertEqual(expected.id, generated_node.data.id)
            self.assertEqual(expected.content, generated_node.data.content)

if __name__ == '__main__':
    unittest.main()
