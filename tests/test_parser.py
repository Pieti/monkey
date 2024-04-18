from typing import Any

import pytest
from monkey import ast
from monkey.lexer import Lexer
from monkey.parser import Parser


def _test_integer_literal(exp: ast.Expression, value: int) -> None:
    assert isinstance(exp, ast.IntegerLiteral)
    assert exp.value == value
    assert exp.token.literal == str(value)


def _test_identifier(exp: ast.Expression, value: str) -> None:
    assert isinstance(exp, ast.Identifier)
    assert exp.value == value
    assert exp.token.literal == value


def _test_boolean(exp: ast.Expression, value: bool) -> None:
    assert isinstance(exp, ast.Boolean)
    assert exp.value == value
    assert exp.token.literal == str(value).lower()


def _test_literal_expression(exp: ast.Expression, expected: Any) -> None:
    if expected in (True, False):
        _test_boolean(exp, expected)
    elif isinstance(expected, int):
        _test_integer_literal(exp, expected)
    elif isinstance(expected, str):
        _test_identifier(exp, expected)
    else:
        raise ValueError(f"Type of exp not handled. Got={type(expected)}")


def _test_let_statement(stmt: ast.Statement, name: str) -> None:
    assert isinstance(stmt, ast.LetStatement)
    assert stmt.token.literal == "let"
    assert stmt.name.value == name
    assert stmt.name.token.literal == name


def _test_infix_expression(
    exp: ast.Expression, left: Any, operator: str, right: Any
) -> None:
    assert isinstance(exp, ast.InfixExpression)
    _test_literal_expression(exp.left, left)
    assert exp.operator == operator
    _test_literal_expression(exp.right, right)


def _test_prefix_expression(exp: ast.Expression, operator: str, value: Any) -> None:
    assert isinstance(exp, ast.PrefixExpression)
    assert exp.operator == operator
    _test_literal_expression(exp.right, value)


@pytest.mark.parametrize(
    "input, expected_ident, expected_value",
    [
        (
            "let x = 5;",
            "x",
            5,
        ),
        (
            "let y = true;",
            "y",
            True,
        ),
        (
            "let foobar = y;",
            "foobar",
            "y",
        ),
    ],
)
def test_let_statements(input: str, expected_ident: str, expected_value: Any) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    let_stmt = program.statements[0]
    assert isinstance(let_stmt, ast.LetStatement)
    _test_let_statement(let_stmt, expected_ident)
    _test_literal_expression(let_stmt.value, expected_value)


@pytest.mark.parametrize(
    "input",
    [
        ("return 5;"),
        ("return 10;"),
        ("return 993322;"),
    ],
)
def test_return_statements(input: str) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    return_stmt = program.statements[0]
    assert str(return_stmt) == input
    assert return_stmt.token.literal == "return"
    assert isinstance(return_stmt, ast.ReturnStatement)


def test_identifier_expression() -> None:
    input = "foobar;"

    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.Identifier)
    assert stmt.expression.value == "foobar"
    assert stmt.expression.token.literal == "foobar"


@pytest.mark.parametrize(
    "input, value, literal",
    [
        (
            "true;",
            True,
            "true",
        ),
        (
            "false;",
            False,
            "false",
        ),
    ],
)
def test_boolean_expression(input: str, value: bool, literal: str) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.Boolean)
    assert stmt.expression.value == value
    assert stmt.expression.token.literal == literal


def test_integer_literal_expression() -> None:
    input = "5;"
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.IntegerLiteral)
    assert stmt.expression.value == 5
    assert stmt.expression.token.literal == "5"


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "-a * b",
            "((-a) * b)",
        ),
        (
            "!-a",
            "(!(-a))",
        ),
        (
            "a + b + c",
            "((a + b) + c)",
        ),
        (
            "a + b - c",
            "((a + b) - c)",
        ),
        (
            "a * b * c",
            "((a * b) * c)",
        ),
        (
            "a * b / c",
            "((a * b) / c)",
        ),
        (
            "a + b / c",
            "(a + (b / c))",
        ),
        (
            "a + b * c + d / e - f",
            "(((a + (b * c)) + (d / e)) - f)",
        ),
        (
            "3 + 4; -5 * 5",
            "(3 + 4)((-5) * 5)",
        ),
        (
            "5 > 4 == 3 < 4",
            "((5 > 4) == (3 < 4))",
        ),
        (
            "5 < 4 != 3 > 4",
            "((5 < 4) != (3 > 4))",
        ),
        (
            "3 + 4 * 5 == 3 * 1 + 4 * 5",
            "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",
        ),
        (
            "true",
            "true",
        ),
        (
            "false",
            "false",
        ),
        (
            "3 > 5 == false",
            "((3 > 5) == false)",
        ),
        (
            "3 < 5 == true",
            "((3 < 5) == true)",
        ),
        (
            "1 + (2 + 3) + 4",
            "((1 + (2 + 3)) + 4)",
        ),
        (
            "(5 + 5) * 2",
            "((5 + 5) * 2)",
        ),
        (
            "2 / (5 + 5)",
            "(2 / (5 + 5))",
        ),
        (
            "-(5 + 5)",
            "(-(5 + 5))",
        ),
        (
            "!(true == true)",
            "(!(true == true))",
        ),
    ],
)
def test_operator_precedence_parsing(input: str, expected: str) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert str(program) == expected


@pytest.mark.parametrize(
    "input, operator, value",
    [
        (
            "!5;",
            "!",
            5,
        ),
        ("-15;", "-", 15),
        ("!true;", "!", True),
        ("!false;", "!", False),
    ],
)
def test_parsing_prefix_expressions(input: str, operator: str, value: Any) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert stmt.expression is not None
    _test_prefix_expression(stmt.expression, operator, value)


@pytest.mark.parametrize(
    "input, left_value, operator, right_value",
    [
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
        ("true == true", True, "==", True),
        ("true != false", True, "!=", False),
        ("false == false", False, "==", False),
    ],
)
def test_parsing_infix_expressions(
    input: str, left_value: Any, operator: str, right_value: Any
) -> None:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert stmt.expression is not None
    _test_infix_expression(stmt.expression, left_value, operator, right_value)


def test_if_expression() -> None:
    input = "if (x < y) { x }"

    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.IfExpression)


def test_string_literal_expression() -> None:
    input = '"hello world";'

    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.StringLiteral)
    assert stmt.expression.value == "hello world"
