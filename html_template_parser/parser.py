from html_template_parser.lexem import *
from html_template_parser.tokenizer import *
from html_template_parser.action import *

__all__ = [
    'parse'
]


def parse(template, model=None):
    tokenizer = Tokenizer(template)
    parser = Parser(tokenizer, model)

    tree = []
    while True:
        subtree = parser.generate_tree()
        if subtree is None:
            break
        tree.append(subtree)

    generated_html = ''
    for subtree in tree:
        generated_html += subtree.execute()
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
        elif self.current_token.id == Lexem.HTML:
            return self.html_code()
        elif self.current_token.id == Lexem.STATEMENT_OPEN:
            return self.statement()
        elif self.current_token.id == Lexem.PRINT_OPEN:
            return self.print()
        elif self.current_token.id == Lexem.COMMENT_OPEN:
            return self.comment()
        else:
            raise self.unexpected_token_error()

    def unexpected_token_error(self):
        if self.current_token.content:
            unexpected = self.current_token.content
        else:
            unexpected = keywords.get(self.current_token.id) or symbols.get(self.current_token.id)
        return ParserSyntaxError('Unexpected "{}"'.format(unexpected), self.current_token.line, self.current_token.position)

    def accept(self, token_id):
        if self.current_token.id == token_id:
            self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        else:
            expected = reverted_keywords.get(token_id) or reverted_symbols.get(token_id)
            raise ParserSyntaxError('Expected "{}"'.format(expected), self.current_token.line, self.current_token.position)

    def html_code(self):
        node = HTMLCode(self.current_token.content)
        self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        return node

    def comment(self):
        self.accept(Lexem.COMMENT_OPEN)
        comment = self.current_token.content
        self.accept(Lexem.COMMENT)
        self.accept(Lexem.COMMENT_CLOSE)
        return Comment(self.current_token.content)

    def print(self):
        self.accept(Lexem.PRINT_OPEN)
        expression = self.expression()
        self.accept(Lexem.PRINT_CLOSE)
        return PrintStatement(expression)

    def expression(self):
        operand1 = self.mul_div_mod_expression()
        if self.current_token.id == Lexem.PLUS:
            self.accept(Lexem.PLUS)
            operand2 = self.expression()
            return AdditionOperator(operand1, operand2)
        elif self.current_token.id == Lexem.MINUS:
            self.accept(Lexem.MINUS)
            operand2 = self.expression()
            return SubtractionOperator(operand1, operand2)
        else:
            return operand1

    def mul_div_mod_expression(self):
        operand1 = self.factor()
        if self.current_token.id == Lexem.STAR:
            self.accept(Lexem.STAR)
            operand2 = self.mul_div_mod_expression()
            return MultiplicationOperator(operand1, operand2)
        elif self.current_token.id == Lexem.SLASH:
            self.accept(Lexem.SLASH)
            operand2 = self.mul_div_mod_expression()
            return DivisionOperator(operand1, operand2)
        elif self.current_token.id == Lexem.MOD:
            self.accept(Lexem.MOD)
            operand2 = self.mul_div_mod_expression()
            return ModuloOperator(operand1, operand2)
        else:
            return operand1

    def factor(self):
        if self.current_token.id == Lexem.PLUS:
            self.accept(Lexem.PLUS)
            operand = self.factor()
            return PlusOperator(operand)
        elif self.current_token.id == Lexem.MINUS:
            self.accept(Lexem.MINUS)
            operand = self.factor()
            return MinusOperator(operand)
        elif self.current_token.id == Lexem.LEFT_BRACKET:
            self.accept(Lexem.LEFT_BRACKET)
            expression = self.expression()
            self.accept(Lexem.RIGHT_BRACKET)
            return expression
        elif self.current_token.id == Lexem.NUMBER:
            number = self.current_token.content
            self.accept(Lexem.NUMBER)
            return Constant(number)
        elif self.current_token.id == Lexem.INT:
            number = self.current_token.content
            self.accept(Lexem.INT)
            return Constant(number)
        else:
            raise self.unexpected_token_error()
