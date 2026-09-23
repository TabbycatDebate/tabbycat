"""Safe arithmetic helpers for email templates.

These are registered as template builtins (see ``TEMPLATES`` in the settings)
so they are available without a ``{% load %}`` tag, including when notification
subjects/bodies are rendered by the notifications queue consumer.

The intended use is pricing-style calculations inside custom emails, e.g.::

    {% calc "TEAMS_ALLOCATED * 80" %}
    {% calc "TEAMS_ALLOCATED * 80 + ADJUDICATORS_ALLOCATED * 50" %}

or, equivalently, with filters::

    {{ TEAMS_ALLOCATED|mul:80 }}

Only numeric literals, the email's context variables and the operators
``+ - * / // %`` (plus parentheses and unary +/-) are permitted. Anything
else (names that aren't numbers, function calls, exponentiation, etc.)
evaluates to an empty string rather than raising, so a malformed formula can
never break sending a batch of emails.
"""
import ast
import operator

from django import template

register = template.Library()

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _to_number(value):
    """Coerce a context value into an int/float, defaulting to 0."""
    if isinstance(value, (int, float)):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0


def _eval_node(node, names):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, names)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.Name):
        return _to_number(names.get(node.id, 0))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_eval_node(node.left, names), _eval_node(node.right, names))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand, names))
    raise ValueError("Unsupported expression")


def _format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


@register.simple_tag(takes_context=True)
def calc(context, expression):
    """Evaluate a simple arithmetic ``expression`` against the template context.

    Returns an empty string if the expression is invalid so a bad formula
    never blocks an email from being sent.
    """
    try:
        tree = ast.parse(str(expression), mode='eval')
        result = _eval_node(tree, context.flatten())
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError):
        return ''
    return _format_number(result)


@register.filter
def mul(value, arg):
    return _format_number(_to_number(value) * _to_number(arg))


@register.filter
def sub(value, arg):
    return _format_number(_to_number(value) - _to_number(arg))


@register.filter
def div(value, arg):
    divisor = _to_number(arg)
    if divisor == 0:
        return ''
    return _format_number(_to_number(value) / divisor)
