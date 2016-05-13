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
        divisor = self.operand2.execute()
        if divisor == 0:
            raise ParserSemanticError('Division by 0')
        return self.operand1.execute() % divisor


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
