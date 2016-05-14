from html_template_parser.action import *
from html_template_parser.lexem import *
from html_template_parser.tokenizer import *
from html_template_parser.utils import *

__all__ = [
    'parse'
]


def parse(template, csv_model=None):
    tokenizer = Tokenizer(template)
    parser = Parser(tokenizer, csv_model)

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


class ScopeContext:
    def __init__(self, csv_model):
        self.model = {'csv': []}
        if csv_model:
            import csv
            with open(csv_model) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row = convert_strings_to_numbers(row)
                    self.model['csv'].append(row)

    def find(self, identifier):
        try:
            return self.model[identifier]
        except KeyError:
            raise ParserSemanticError('Unknown identifier \'{}\''.format(identifier))

    def add(self, identifier, value):
        self.model[identifier] = value

    def push(self):
        pass

    def pop(self):
        pass

class Parser:
    def __init__(self, tokenizer, csv_model):
        self.tokenizer = tokenizer
        self.current_token = self.tokenizer.get_next_token(omit_whitespace=True)
        self.scope_context = ScopeContext(csv_model)

    class StatementClose(Exception):
        def __init__(self):
            Exception.__init__(self)

    def generate_tree(self):
        """Generate parse tree."""
        if self.current_token.id == Lexem.HTML:
            return self.html_code()
        elif self.current_token.id == Lexem.STATEMENT_OPEN:
            return self.statement()
        elif self.current_token.id == Lexem.PRINT_OPEN:
            return self.print()
        elif self.current_token.id == Lexem.COMMENT_OPEN:
            return self.comment()
        elif self.current_token.id == Lexem.EOI:
            return None
        else:
            raise self.unexpected_token_error()

    def accept(self, token_id, omit_whitespace=True):
        if self.current_token.id == token_id:
            self.current_token = self.tokenizer.get_next_token(omit_whitespace)
        else:
            expected = reverted_keywords.get(token_id) or reverted_symbols.get(token_id)
            raise ParserSyntaxError('Expected "{}"'.format(expected), self.current_token.line, self.current_token.position)

    def unexpected_token_error(self):
        if self.current_token.content:
            unexpected = self.current_token.content
        elif self.current_token.id == Lexem.EOI:
            unexpected = 'EOI'
        else:
            unexpected = reverted_keywords.get(self.current_token.id) or reverted_symbols.get(self.current_token.id)
        return ParserSyntaxError('Unexpected "{}"'.format(unexpected), self.current_token.line, self.current_token.position)

    def html_code(self):
        node = HTMLCode(self.current_token.content)
        self.accept(Lexem.HTML)
        return node

    def comment(self):
        self.accept(Lexem.COMMENT_OPEN)
        comment = self.current_token.content
        self.accept(Lexem.COMMENT)
        self.accept(Lexem.COMMENT_CLOSE)
        return Comment(comment)

    def statement(self):
        self.accept(Lexem.STATEMENT_OPEN)
        if self.current_token.id == Lexem.IF:
            return self.if_statement()
        elif self.current_token.id == Lexem.FOR:
            return self.for_statement()
        elif self.current_token.id == Lexem.SET:
            return self.set_statement()
        elif self.current_token.id == Lexem.MACRO:
            return self.macro_statement()
        elif self.current_token.id in [Lexem.ENDIF, Lexem.ELSE, Lexem.ELIF, Lexem.ENDFOR, Lexem.ENDMACRO]:
            raise self.StatementClose()
        else:
            raise self.unexpected_token_error()

    def if_statement(self):
        self.accept(Lexem.IF)
        comp_expression = self.expression()
        self.accept(Lexem.STATEMENT_CLOSE)
        inside_statements = self.get_statements()
        if self.current_token.id == Lexem.ENDIF:
            self.accept(Lexem.ENDIF)
            self.accept(Lexem.STATEMENT_CLOSE)
            else_statements = None
        elif self.current_token.id == Lexem.ELSE:
            self.accept(Lexem.ELSE)
            self.accept(Lexem.STATEMENT_CLOSE)
            else_statements = self.get_statements()
            if self.current_token.id == Lexem.ENDIF:
                self.accept(Lexem.ENDIF)
                self.accept(Lexem.STATEMENT_CLOSE)
            else:
                raise self.unexpected_token_error()
        elif self.current_token.id == Lexem.ELIF:
            self.current_token.id = Lexem.IF
            else_statements = [self.if_statement()]
        else:
            raise self.unexpected_token_error()
        return IfStatement(comp_expression, inside_statements, else_statements)

    def for_statement(self):
        self.accept(Lexem.FOR)
        identifier = self.current_token.content
        self.accept(Lexem.IDENTIFIER)
        self.accept(Lexem.IN)
        collection = self.expression()
        self.accept(Lexem.STATEMENT_CLOSE)
        inside_statements = self.get_statements()
        if self.current_token.id == Lexem.ENDFOR:
            self.accept(Lexem.ENDFOR)
            self.accept(Lexem.STATEMENT_CLOSE)
        else:
            raise self.unexpected_token_error()
        return ForStatement(identifier, collection, inside_statements, self.scope_context)

    def set_statement(self):
        self.accept(Lexem.SET)
        identifier = self.current_token.content
        self.accept(Lexem.IDENTIFIER)
        self.accept(Lexem.ASSIGN)
        value = self.expression()
        self.accept(Lexem.STATEMENT_CLOSE)
        return SetStatement(identifier, value, self.scope_context)

    def macro_statement(self):
        self.accept(Lexem.MACRO)
        identifier = self.current_token.content
        self.accept(Lexem.IDENTIFIER, omit_whitespace=False)
        args = self.arguments(declaration=True)
        self.accept(Lexem.STATEMENT_CLOSE)
        inside_statements = self.get_statements()
        if self.current_token.id == Lexem.ENDMACRO:
            self.accept(Lexem.ENDMACRO)
            self.accept(Lexem.STATEMENT_CLOSE)
        else:
            raise self.unexpected_token_error()
        return MacroStatement(identifier, args, inside_statements, self.scope_context)

    def get_statements(self):
        statements = []
        while True:
            try:
                statement = self.generate_tree()
                if statement is None:
                    raise self.unexpected_token_error()
                statements.append(statement)
            except self.StatementClose:
                return statements

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
            name = self.current_token.content
            self.accept(Lexem.IDENTIFIER, omit_whitespace=False)
            if self.current_token.id == Lexem.LEFT_BRACKET:
                return MacroCall(name, self.scope_context, self.arguments())
            elif self.current_token.id == Lexem.LEFT_SQUARE_BRACKET:
                return self.indexing(Variable(name, self.scope_context))
            else:
                self.accept(Lexem.WHITESPACE)
                return Variable(name, self.scope_context)
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

    def indexing(self, variable):
        self.accept(Lexem.LEFT_SQUARE_BRACKET)
        index = self.expression()
        self.accept(Lexem.RIGHT_SQUARE_BRACKET)
        if self.current_token.id == Lexem.LEFT_SQUARE_BRACKET:
            return self.indexing(Indexing(variable, index))
        else:
            return Indexing(variable, index)

    def arguments(self, declaration=False):
        self.accept(Lexem.LEFT_BRACKET)
        args = []
        while True:
            if self.current_token.id == Lexem.RIGHT_BRACKET:
                self.accept(Lexem.RIGHT_BRACKET)
                return args
            elif declaration:
                arg = self.current_token.content
                self.accept(Lexem.IDENTIFIER)
                args.append(arg)
            else:
                arg = self.expression()
                args.append(arg)
            if self.current_token.id != Lexem.RIGHT_BRACKET:
                self.accept(Lexem.COMMA)
