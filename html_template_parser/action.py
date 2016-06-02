import abc
from html_template_parser.error import *
from html_template_parser.utils import *


def push_stack(func):
    def func_wrapper(*args):
        scope_context = args[1]
        scope_context.push()
        result = func(*args)
        scope_context.pop()
        return result
    return func_wrapper


class ScopeContext:
    def __init__(self, model=None, format='csv'):
        self.model = [{'model': []}]
        if model:
            self._load_model(model, format)

    def _load_model(self, model, format):
        if format is 'csv':
            with open(model) as f:
                import csv
                reader = csv.DictReader(f)
                for row in reader:
                    row = convert_strings_to_numbers(row)
                    self.model[0]['model'].append(row)
        elif format is 'json':
            with open(model) as f:
                import json
                self.model.append(json.load(f))
        elif format is 'yaml':
            with open(model) as f:
                import yaml
                self.model.append(yaml.load(f))
        else:
            raise ParserArgumentError('Invalid argument value \'{}\''.format(format))

    def find(self, identifier):
            for level in reversed(self.model):
                try:
                    return level[identifier]
                except KeyError:
                    pass
            raise UnknownIdentifier('Unknown identifier \'{}\''.format(identifier))

    def add(self, identifier, value):
        self.model[-1][identifier] = value

    def push(self):
        self.model.append({})

    def pop(self):
        self.model.pop()


class ParserNode:
    line = None

    def execute(self, scope_context):
        try:
            return self.do_execute(scope_context)
        except (TypeError, ZeroDivisionError, UnknownIdentifier) as exc:
            raise ParserSemanticError(exc, self.line)
        except KeyError as exc:
            raise ParserSemanticError('Unknown key {}'.format(exc), self.line)

    @abc.abstractmethod
    def do_execute(self, scope_context):
        pass


class RootNode(ParserNode):
    def __init__(self, subtrees):
        self.subtrees = subtrees

    def do_execute(self, scope_context):
        generated_html = ''
        for subtree in self.subtrees:
            generated_html += subtree.do_execute(scope_context)
        return generated_html


class Constant(ParserNode):
    def __init__(self, value):
        self.value = value

    def do_execute(self, scope_context):
        return self.value


class Variable(ParserNode):
    def __init__(self, identifier):
        self.identifier = identifier

    def do_execute(self, scope_context):
        return scope_context.find(self.identifier)


class Indexing(ParserNode):
    def __init__(self, variable, index):
        self.variable = variable
        self.index = index

    def do_execute(self, scope_context):
        return self.variable.do_execute(scope_context)[self.index.do_execute(scope_context)]


class AdditionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) + self.operand2.do_execute(scope_context)


class SubtractionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) - self.operand2.do_execute(scope_context)


class MultiplicationOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) * self.operand2.do_execute(scope_context)


class DivisionOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) / self.operand2.do_execute(scope_context)


class ModuloOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) % self.operand2.do_execute(scope_context)


class NotEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) != self.operand2.do_execute(scope_context)


class EqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) == self.operand2.do_execute(scope_context)


class LowerOrEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) <= self.operand2.do_execute(scope_context)


class GreaterOrEqualOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) >= self.operand2.do_execute(scope_context)


class LowerOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) < self.operand2.do_execute(scope_context)


class GreaterOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) > self.operand2.do_execute(scope_context)


class NotOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def do_execute(self, scope_context):
        return not self.operand.do_execute(scope_context)


class OrOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) or self.operand2.do_execute(scope_context)


class AndOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) and self.operand2.do_execute(scope_context)


class MinusOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def do_execute(self, scope_context):
        return -self.operand.do_execute(scope_context)


class PlusOperator(ParserNode):
    def __init__(self, operand):
        self.operand = operand

    def do_execute(self, scope_context):
        return +self.operand.do_execute(scope_context)


class InOperator(ParserNode):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2

    def do_execute(self, scope_context):
        return self.operand1.do_execute(scope_context) in self.operand2.do_execute(scope_context)


class HTMLCode(ParserNode):
    def __init__(self, html):
        self.html = html

    def do_execute(self, scope_context):
        return self.html


class PrintStatement(ParserNode):
    def __init__(self, expression):
        self.expression = expression

    def do_execute(self, scope_context):
        return str(self.expression.execute(scope_context))


class IfStatement(ParserNode):
    def __init__(self, comp_expression, inside_statements, else_statement):
        self.comp_expression = comp_expression
        self.inside_statements = inside_statements
        self.else_statement = else_statement

    @push_stack
    def do_execute(self, scope_context):
        result = ''
        if self.comp_expression.execute(scope_context):
            for statement in self.inside_statements:
                result += statement.execute(scope_context)
        elif self.else_statement:
            for statement in self.else_statement:
                result += statement.execute(scope_context)
        return result


class ForStatement(ParserNode):
    def __init__(self, identifier, collection, inside_statements):
        self.identifier = identifier
        self.collection = collection
        self.inside_statements = inside_statements

    @push_stack
    def do_execute(self, scope_context):
        result = ''
        for element in self.collection.execute(scope_context):
            scope_context.add(self.identifier, element)
            for statement in self.inside_statements:
                result += statement.execute(scope_context)
        return result


class SetStatement(ParserNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def do_execute(self, scope_context):
        scope_context.add(self.identifier, self.value.execute(scope_context))
        return ''


class MacroStatement(ParserNode):
    def __init__(self, identifier, args_name, inside_statements):
        self.identifier = identifier
        self.args_name = args_name
        self.inside_statements = inside_statements

    def do_execute(self, scope_context):
        scope_context.add(self.identifier, self)
        return ''

    @push_stack
    def __call__(self, *args, **kwargs):
        scope_context = args[0]
        for i, arg_name in enumerate(self.args_name):
            scope_context.add(arg_name, args[1][i].execute(scope_context))
        result = ''
        for statement in self.inside_statements:
            result += statement.execute(scope_context)
        return result


class MacroCall(ParserNode):
    def __init__(self, identifier, *args):
        self.identifier = identifier
        self.args = args

    def do_execute(self, scope_context):
        return scope_context.find(self.identifier)(scope_context, *self.args)
