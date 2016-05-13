from html_template_parser.action import *
from html_template_parser.lexem import *
from html_template_parser.tokenizer import *

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
        """Generate parse tree."""
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
        return Comment(comment)

    def print(self):
        self.accept(Lexem.PRINT_OPEN)
        expression = self.expression()
        self.accept(Lexem.PRINT_CLOSE)
        return PrintStatement(expression)

    def expression(self):
        return self.or_expression()

    def or_expression(self):
        operand1 = self.and_expression()
        if self.current_token.id == Lexem.OR:
            self.accept(Lexem.OR)
            operand2 = self.or_expression()
            return OrOperator(operand1, operand2)
        else:
            return operand1

    def and_expression(self):
        operand1 = self.not_expression()
        if self.current_token.id == Lexem.AND:
            self.accept(Lexem.AND)
            operand2 = self.and_expression()
            return AndOperator(operand1, operand2)
        else:
            return operand1

    def not_expression(self):
        if self.current_token.id == Lexem.NOT:
            self.accept(Lexem.NOT)
            operand1 = self.not_expression()
            return NotOperator(operand1)
        else:
            return self.comparison_expression()

    def comparison_expression(self):
        operand1 = self.add_sub_expression()
        if self.current_token.id == Lexem.IN:
            self.accept(Lexem.IN)
            operand2 = self.add_sub_expression()
            return InOperator(operand1, operand2)
        elif self.current_token.id == Lexem.LT:
            self.accept(Lexem.LT)
            operand2 = self.comparison_expression()
            return LowerOperator(operand1, operand2)
        elif self.current_token.id == Lexem.GT:
            self.accept(Lexem.GT)
            operand2 = self.comparison_expression()
            return GreaterOperator(operand1, operand2)
        elif self.current_token.id == Lexem.LE:
            self.accept(Lexem.LE)
            operand2 = self.comparison_expression()
            return LowerOrEqualOperator(operand1, operand2)
        elif self.current_token.id == Lexem.GE:
            self.accept(Lexem.GE)
            operand2 = self.comparison_expression()
            return GreaterOrEqualOperator(operand1, operand2)
        elif self.current_token.id == Lexem.EQ:
            self.accept(Lexem.EQ)
            operand2 = self.comparison_expression()
            return EqualOperator(operand1, operand2)
        elif self.current_token.id == Lexem.NEQ:
            self.accept(Lexem.NEQ)
            operand2 = self.comparison_expression()
            return NotEqualOperator(operand1, operand2)
        else:
            return operand1

    def add_sub_expression(self):
        operand1 = self.mul_div_mod_expression()
        if self.current_token.id == Lexem.PLUS:
            self.accept(Lexem.PLUS)
            operand2 = self.add_sub_expression()
            return AdditionOperator(operand1, operand2)
        elif self.current_token.id == Lexem.MINUS:
            self.accept(Lexem.MINUS)
            operand2 = self.add_sub_expression()
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
        elif self.current_token.id == Lexem.IDENTIFIER:
            # TODO do it
            raise NotImplementedError
        else:
            return self.constant()

    def constant(self):
        if self.current_token.id == Lexem.NUMBER:
            number = self.current_token.content
            self.accept(Lexem.NUMBER)
            return Constant(number)
        elif self.current_token.id == Lexem.INT:
            number = self.current_token.content
            self.accept(Lexem.INT)
            return Constant(number)
        elif self.current_token.id == Lexem.STRING:
            string = self.current_token.content
            self.accept(Lexem.STRING)
            return Constant(string)
        elif self.current_token.id == Lexem.TRUE:
            self.accept(Lexem.TRUE)
            return Constant(True)
        elif self.current_token.id == Lexem.FALSE:
            self.accept(Lexem.FALSE)
            return Constant(False)
        else:
            raise self.unexpected_token_error()
