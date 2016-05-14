import abc
from html_template_parser.error import *


class ParserNode:
    @abc.abstractmethod
    def execute(self):
        pass


class HTMLCode(ParserNode):
    def __init__(self, html):
        self.html = html

    def execute(self):
        return self.html


class Comment(ParserNode):
    def __init__(self, comment):
        self.comment = comment

    def execute(self):
        return ''


class Constant(ParserNode):
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class Variable(ParserNode):
    def __init__(self, identifier, scope_context):
        self.identifier = identifier
        self.scope_context = scope_context

    def execute(self):
        return self.scope_context.find(self.identifier)


class Indexing(ParserNode):
    def __init__(self, variable, index):
        self.variable = variable
        self.index = index

    def execute(self):
        try:
            return self.variable.execute()[self.index.execute()]
        except KeyError as exc:
            raise ParserSemanticError('Unknown key {}'.format(exc))


class PrintStatement(ParserNode):
    def __init__(self, expression):
        self.expression = expression

    def execute(self):
        return str(self.expression.execute())


class AdditionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() + self.operand2.execute()


class SubtractionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() - self.operand2.execute()


class MultiplicationOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() * self.operand2.execute()


class DivisionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        try:
            return self.operand1.execute() / self.operand2.execute()
        except ZeroDivisionError as exc:
            raise ParserSemanticError(exc)


class ModuloOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        try:
            return self.operand1.execute() % self.operand2.execute()
        except ZeroDivisionError as exc:
            raise ParserSemanticError(exc)


class NotEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() != self.operand2.execute()


class EqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() == self.operand2.execute()


class LowerOrEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() <= self.operand2.execute()


class GreaterOrEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() >= self.operand2.execute()


class LowerOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() < self.operand2.execute()


class GreaterOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() > self.operand2.execute()


class NotOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def execute(self):
        return not self.operand.execute()


class OrOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() or self.operand2.execute()


class AndOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        return self.operand1.execute() and self.operand2.execute()


class MinusOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def execute(self):
        return -self.operand.execute()


class PlusOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def execute(self):
        return +self.operand.execute()


class InOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def execute(self):
        try:
            return self.operand1.execute() in self.operand2.execute()
        except TypeError as exc:
            raise ParserSemanticError(exc)


class IfStatement(ParserNode):
    def __init__(self, comp_expression, inside_statements, else_statement):
        self.comp_expression = comp_expression
        self.inside_statements = inside_statements
        self.else_statement = else_statement

    def execute(self):
        result = ''
        if self.comp_expression.execute():
            for statement in self.inside_statements:
                result += statement.execute()
        elif self.else_statement:
            for statement in self.else_statement:
                result += statement.execute()
        return result


class ForStatement(ParserNode):
    def __init__(self, identifier, collection, inside_statements, scope_context):
        self.identifier = identifier
        self.collection = collection
        self.inside_statements = inside_statements
        self.scope_context = scope_context

    def execute(self):
        result = ''
        for element in self.collection.execute():
            self.scope_context.add(self.identifier, element)
            for statement in self.inside_statements:
                result += statement.execute()
        return result


class SetStatement(ParserNode):
    def __init__(self, identifier, value, scope_context):
        self.identifier = identifier
        self.value = value
        self.scope_context = scope_context

    def execute(self):
        self.scope_context.add(self.identifier, self.value.execute())
        return ''


class MacroStatement(ParserNode):
    def __init__(self, identifier, args_name, inside_statements, scope_context):
        self.identifier = identifier
        self.args_name = args_name
        self.inside_statements = inside_statements
        self.scope_context = scope_context

    def execute(self):
        self.scope_context.add(self.identifier, self)
        return ''

    def __call__(self, *args, **kwargs):
        for i, arg_name in enumerate(self.args_name):
            self.scope_context.add(arg_name, args[0][i].execute())
        result = ''
        for statement in self.inside_statements:
            result += statement.execute()
        return result


class MacroCall(ParserNode):
    def __init__(self, identifier, scope_context, *args):
        self.identifier = identifier
        self.args = args
        self.scope_context = scope_context

    def execute(self):
        return self.scope_context.find(self.identifier)(*self.args)
