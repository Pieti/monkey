from monkey import ast
from monkey.builtins import BUILTINS
from monkey.environment import Environment
from monkey.mobj import (FALSE, NULL, TRUE, Array, Builtin, Error, Function,
                         Hash, Hashable, HashKey, HashPair, Integer,
                         MonkeyObject, ReturnValue, String)


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
    elif isinstance(node, ast.StringLiteral):
        return String(node.value)
    elif isinstance(node, ast.ArrayLiteral):
        elements = _eval_expressions(node.elements, env)
        if len(elements) == 1 and isinstance(elements[0], Error):
            return elements[0]
        return Array(elements)
    elif isinstance(node, ast.HashLiteral):
        return _eval_hash_literal(node, env)
    elif isinstance(node, ast.IndexExpression):
        left = monkey_eval(node.left, env)
        if isinstance(left, Error):
            return left
        index = monkey_eval(node.index, env)
        if isinstance(index, Error):
            return index
        return _eval_index_expression(left, index)
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
    if isinstance(left, String) and isinstance(right, String):
        return _eval_string_infix_expression(operator, left, right)
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


def _eval_string_infix_expression(
    operator: str, left: String, right: String
) -> MonkeyObject:
    if operator != "+":
        return Error(
            f"unknown operator: {left.monkey_type} {operator} {right.monkey_type}"
        )
    return String(left.value + right.value)


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

    value = BUILTINS.get(node.value)
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


def _eval_index_expression(left: MonkeyObject, index: MonkeyObject) -> MonkeyObject:
    if isinstance(left, Array) and isinstance(index, Integer):
        return _eval_array_index_expression(left, index)
    if isinstance(left, Hash):
        return _eval_hash_index_expression(left, index)
    return Error(f"index operator not supported: {left.monkey_type}")


def _eval_array_index_expression(array: Array, index: Integer) -> MonkeyObject:
    idx = index.value
    max = len(array.elements) - 1
    if idx < 0 or idx > max:
        return NULL
    return array.elements[idx]


def _eval_hash_index_expression(hash: Hash, index: MonkeyObject) -> MonkeyObject:
    if not isinstance(index, Hashable):
        return Error(f"unusable as hash key: {index.monkey_type}")
    pair = hash.pairs.get(index.hash_key())
    if pair is None:
        return NULL
    return pair.value


def _eval_hash_literal(node: ast.HashLiteral, env: Environment) -> MonkeyObject:
    pairs: dict[HashKey, HashPair] = {}
    for key_node, value_node in node.pairs.items():
        key = monkey_eval(key_node, env)
        if isinstance(key, Error):
            return key
        if not isinstance(key, Hashable):
            return Error(f"unusable as hash key: {key.monkey_type}")
        value = monkey_eval(value_node, env)
        if isinstance(value, Error):
            return value
        hashed = key.hash_key()
        pairs[hashed] = HashPair(key, value)
    return Hash(pairs)


def _apply_function(fn: MonkeyObject, args: list[MonkeyObject]) -> MonkeyObject:
    if isinstance(fn, Function):
        extended_env = _extend_function_env(fn, args)
        evaluated = monkey_eval(fn.body, extended_env)
        return _unwrap_return_value(evaluated)
    elif isinstance(fn, Builtin):
        return fn(*args)
    else:
        return Error(f"not a function: {fn.monkey_type}")


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
