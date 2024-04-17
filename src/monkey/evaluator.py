from monkey import ast
from monkey.environment import Environment
from monkey.mobj import (FALSE, NULL, TRUE, Error, Function, Integer,
                         MonkeyObject, ReturnValue)


def monkey_eval(node: ast.Node, env: Environment) -> MonkeyObject:
    if isinstance(node, ast.Program):
        return _eval_program(node, env)
    elif isinstance(node, ast.ExpressionStatement):
        return monkey_eval(node.expression, env)
    elif isinstance(node, ast.BlockStatement):
        return _eval_block_statement(node, env)
    elif isinstance(node, ast.LetStatement):
        value = monkey_eval(node.value, env)
        if isinstance(value, Error):
            return value
        env.put(node.name.value, value)
        return value
    elif isinstance(node, ast.ReturnStatement):
        value = monkey_eval(node.value, env)
        if isinstance(value, Error):
            return value
        return ReturnValue(value)
    elif isinstance(node, ast.IfExpression):
        return _eval_if_expression(node, env)
    elif isinstance(node, ast.Identifier):
        return _eval_identifier(node, env)
    elif isinstance(node, ast.IntegerLiteral):
        return Integer(node.value)
    elif isinstance(node, ast.Boolean):
        return TRUE if node.value else FALSE
    elif isinstance(node, ast.PrefixExpression):
        right = monkey_eval(node.right, env)
        if isinstance(right, Error):
            return right
        return _eval_prefix_expression(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = monkey_eval(node.left, env)
        if isinstance(left, Error):
            return left
        right = monkey_eval(node.right, env)
        if isinstance(right, Error):
            return right
        return _eval_infix_expression(node.operator, left, right)
    elif isinstance(node, ast.FunctionLiteral):
        return Function(node.parameters, node.body, env)
    elif isinstance(node, ast.CallExpression):
        function = monkey_eval(node.function, env)
        if isinstance(function, Error):
            return function
        args = _eval_expressions(node.arguments, env)
        if len(args) == 1 and isinstance(args[0], Error):
            return args[0]
        return _apply_function(function, args)
    return NULL


def _eval_program(program: ast.Program, env: Environment) -> MonkeyObject:
    result = None
    for stmt in program.statements:
        result = monkey_eval(stmt, env)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, Error):
            return result
    assert result is not None
    return result


def _eval_block_statement(block: ast.BlockStatement, env: Environment) -> MonkeyObject:
    result = None
    for stmt in block.statements:
        result = monkey_eval(stmt, env)
        if result is not None:
            if isinstance(result, ReturnValue) or isinstance(result, Error):
                return result
    assert result is not None
    return result


def _eval_prefix_expression(operator: str, right: MonkeyObject) -> MonkeyObject:
    if operator == "!":
        return _eval_bang_operator_expression(right)
    if operator == "-":
        return _eval_minus_prefix_operator_expression(right)
    return Error(f"unknown operator: {operator}{right.monkey_type}")


def _eval_bang_operator_expression(right: MonkeyObject) -> MonkeyObject:
    if right is TRUE:
        return FALSE
    if right is FALSE:
        return TRUE
    if right is NULL:
        return TRUE
    return FALSE


def _eval_minus_prefix_operator_expression(right: MonkeyObject) -> MonkeyObject:
    if not isinstance(right, Integer):
        return Error(f"unknown operator: -{right.monkey_type}")
    return Integer(-right.value)


def _eval_infix_expression(
    operator: str, left: MonkeyObject, right: MonkeyObject
) -> MonkeyObject:
    if isinstance(left, Integer) and isinstance(right, Integer):
        return _eval_integer_infix_expression(operator, left, right)
    if operator == "==":
        return TRUE if left is right else FALSE
    if operator == "!=":
        return TRUE if left is not right else FALSE
    if left.monkey_type != right.monkey_type:
        return Error(
            f"type mismatch: {left.monkey_type} {operator} {right.monkey_type}"
        )
    return Error(f"unknown operator: {left.monkey_type} {operator} {right.monkey_type}")


def _eval_integer_infix_expression(
    operator: str, left: Integer, right: Integer
) -> MonkeyObject:
    if operator == "+":
        return Integer(left.value + right.value)
    if operator == "-":
        return Integer(left.value - right.value)
    if operator == "*":
        return Integer(left.value * right.value)
    if operator == "/":
        return Integer(left.value // right.value)
    if operator == "<":
        return TRUE if left.value < right.value else FALSE
    if operator == ">":
        return TRUE if left.value > right.value else FALSE
    if operator == "==":
        return TRUE if left.value == right.value else FALSE
    if operator == "!=":
        return TRUE if left.value != right.value else FALSE
    return Error(f"unknown operator: {left.monkey_type} {operator} {right.monkey_type}")


def _eval_if_expression(ie: ast.IfExpression, env: Environment) -> MonkeyObject:
    condition = monkey_eval(ie.condition, env)
    if isinstance(condition, Error):
        return condition

    if is_truthy(condition):
        return monkey_eval(ie.consequence, env)
    if ie.alternative is not None:
        return monkey_eval(ie.alternative, env)
    return NULL


def _eval_identifier(node: ast.Identifier, env: Environment) -> MonkeyObject:
    value = env.get(node.value)
    if value is not None:
        return value
    return Error(f"identifier not found: {node.value}")


def _eval_expressions(
    expressions: list[ast.Expression], env: Environment
) -> list[MonkeyObject]:
    result = []
    for expr in expressions:
        evaluated = monkey_eval(expr, env)
        if isinstance(evaluated, Error):
            return [evaluated]
        result.append(evaluated)
    return result


def _apply_function(fn: MonkeyObject, args: list[MonkeyObject]) -> MonkeyObject:
    if not isinstance(fn, Function):
        return Error(f"not a function {fn.monkey_type}")

    extended_env = _extend_function_env(fn, args)
    evaluated = monkey_eval(fn.body, extended_env)
    return _unwrap_return_value(evaluated)


def _extend_function_env(fn: Function, args: list[MonkeyObject]) -> Environment:
    env = Environment(outer=fn.env)
    for param, arg in zip(fn.parameters, args):
        env.put(param.value, arg)
    return env


def _unwrap_return_value(obj: MonkeyObject) -> MonkeyObject:
    if isinstance(obj, ReturnValue):
        return obj.value
    return obj


def is_truthy(obj: MonkeyObject) -> bool:
    return obj is not FALSE and obj is not NULL
