import abc
from treelib import Tree, Node

from html_template_parser.tokenizer import SourceController, Tokenizer

__all__ = [
    'parse'
]


def parse(template, model=None):
    tokenizer = Tokenizer(SourceController(template))
    tree = generate_tree(tokenizer.get_tokens(omit_whitespace=True))


def generate_tree(tokens):
    """Generate parse tree. Tokens should not contain whitespace tokens."""
    tree = Tree()
    tree.add_node(Node(data=next(tokens)))

    #print(tree.get_node(tree.root).data)
    return tree


@ab
class ParserNode(Node):
    def execute(self):
