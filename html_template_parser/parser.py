import abc

from treelib import Tree, Node

from html_template_parser.error import ParserException
from html_template_parser.lexem import Lexem, keywords, symbols
from html_template_parser.tokenizer import Tokenizer, Token

__all__ = [
    'parse'
]


def parse(template, model=None):
    tokenizer = Tokenizer(template)
    parser = Parser(tokenizer, model)
    trees = []
    while True:
        tree = parser.generate_tree()
        if tree is None:
            break
        trees.append(tree)

    generated_html = ''
    for tree in trees:
        generated_html += tree.get_node(tree.root).execute()
    return generated_html


class Parser:
    def __init__(self, tokenizer, model):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        self.model = model  # TODO make table from it

    def generate_tree(self):
        """Generate parse tree. Tokens should not contain whitespace tokens."""
        if self.current_token.id == Lexem.EOI:
            return None
        if self.current_token.id == Lexem.HTML:
            return self.html_code()
        elif self.current_token.id == Lexem.TEMPLATE_OPEN:
            return self.template()
        elif self.current_token.id == Lexem.STATEMENT_OPEN:
            return self.statement()
        elif self.current_token.id == Lexem.COMMENT_OPEN:
            return self.comment()

        if self.current_token.content:
            unexpected = self.current_token.content
        else:
            unexpected = keywords.get(self.current_token.id) or symbols.get(self.current_token.id)
        raise ParserException('Unexpected "{}"'.format(unexpected), self.current_token.line, self.current_token.position)

    def accept(self, token):
        if self.current_token == token:
            self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        else:
            expected = keywords.get(token.id) or symbols.get(token.id)
            raise ParserException('Expected "{}"'.format(expected), self.current_token.line, self.current_token.position)

    def html_code(self):
        tree = Tree()
        tree.add_node(HTMLCode(self.current_token.content))
        self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        return tree

    def comment(self):
        self.accept(Token(Lexem.COMMENT_OPEN))
        comment = self.current_token.content
        self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        self.accept(Token(Lexem.COMMENT_CLOSE))
        tree = Tree()
        tree.add_node(Comment(comment))
        return tree


class ParserNode(Node):
    def __init__(self):
        Node.__init__(self)

    @abc.abstractmethod
    def execute(self):
        pass


class HTMLCode(ParserNode):
    def __init__(self, html):
        self.html = html
        ParserNode.__init__(self)

    def execute(self):
        return self.html


class Comment(ParserNode):
    def __init__(self, comment):
        self.comment = comment
        ParserNode.__init__(self)

    def execute(self):
        return ''
