from typing import Any, Optional

import pytest
from monkey.environment import Environment
from monkey.evaluator import monkey_eval
from monkey.lexer import Lexer
from monkey.mobj import (FALSE, NULL, TRUE, Array, Error, Function, Hash,
                         HashPair, Integer, MonkeyObject, String)
from monkey.parser import Parser


def _test_eval(input: str) -> MonkeyObject:
    lexer = Lexer(input)
    parser = Parser(lexer)
    program = parser.parse_program()
    env = Environment()
    return monkey_eval(program, env)


def _test_integer_object(obj: MonkeyObject, expected: int) -> None:
    assert isinstance(obj, Integer)
    assert obj.value == expected


def _test_boolean_object(obj: MonkeyObject, expected: bool) -> None:
    if expected is True:
        assert obj is TRUE
    else:
        assert obj is FALSE


def _test_null_object(obj: MonkeyObject) -> None:
    assert obj is NULL


@pytest.mark.parametrize(
    "input, expected",
    [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
        ("5 / 2", 2),
    ],
)
def test_eval_integer_expression(input: str, expected: int) -> None:
    evaluated = _test_eval(input)
    _test_integer_object(evaluated, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ],
)
def test_eval_boolean_expression(input: str, expected: bool) -> None:
    evaluated = _test_eval(input)
    _test_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ],
)
def test_bang_operator(input: str, expected: bool) -> None:
    evaluated = _test_eval(input)
    _test_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ],
)
def test_if_else_expressions(input: str, expected: Optional[int]) -> None:
    evaluated = _test_eval(input)
    if isinstance(expected, int):
        _test_integer_object(evaluated, expected)
    else:
        _test_null_object(evaluated)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        (
            "if ( 10 > 1) { if (10 > 1) { return 10; } return 1; }",
            10,
        ),
    ],
)
def test_return_statements(input: str, expected: int) -> None:
    evaluated = _test_eval(input)
    _test_integer_object(evaluated, expected)


@pytest.mark.parametrize(
    "input, expected_message",
    [
        (
            "5 + true;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "5 + true; 5;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "-true",
            "unknown operator: -BOOLEAN",
        ),
        (
            "true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "5; true + false; 5",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "if (10 > 1) { true + false; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "if (10 > 1) { if (10 > 1) { return true + false; } return 1; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "foobar",
            "identifier not found: foobar",
        ),
        (
            '"Hello" - "World"',
            "unknown operator: STRING - STRING",
        ),
        (
            '{"name": "Monkey"}[fn(x) { x }];',
            "unusable as hash key: FUNCTION",
        ),
    ],
)
def test_error_handling(input: str, expected_message: str) -> None:
    evaluated = _test_eval(input)
    assert isinstance(evaluated, Error)
    assert evaluated.message == expected_message


@pytest.mark.parametrize(
    "input, expected",
    [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ],
)
def test_let_statements(input: str, expected: int) -> None:
    _test_integer_object(_test_eval(input), expected)


def test_function_object() -> None:
    input = "fn(x) { x + 2; };"
    function = _test_eval(input)
    assert isinstance(function, Function)
    assert len(function.parameters) == 1
    assert str(function.parameters[0]) == "x"

    expected_body = "(x + 2)"
    assert str(function.body) == expected_body


@pytest.mark.parametrize(
    "input, expected",
    [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ],
)
def test_function_application(input: str, expected: int) -> None:
    _test_integer_object(_test_eval(input), expected)


def test_closures() -> None:
    input = """
    let newAdder = fn(x) {
        fn(y) { x + y };
    };

    let addTwo = newAdder(2);
    addTwo(2);
    """

    _test_integer_object(_test_eval(input), 4)


def test_string_literal() -> None:
    input = '"Hello, World!"'
    string = _test_eval(input)
    assert isinstance(string, String)
    assert string.value == "Hello, World!"


def test_string_concatenation() -> None:
    input = '"Hello" + " " + "World!"'

    evaluated = _test_eval(input)
    assert isinstance(evaluated, String)
    assert evaluated.value == "Hello World!"


@pytest.mark.parametrize(
    "input, expected",
    [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
    ],
)
def test_builtin_functions(input: str, expected: Any) -> None:
    evaluated = _test_eval(input)
    if isinstance(expected, int):
        _test_integer_object(evaluated, expected)
    else:
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected


def test_array_literals() -> None:
    input = "[1, 2 * 2, 3 + 3]"

    evaluated = _test_eval(input)
    assert isinstance(evaluated, Array)
    assert len(evaluated.elements) == 3
    _test_integer_object(evaluated.elements[0], 1)
    _test_integer_object(evaluated.elements[1], 4)
    _test_integer_object(evaluated.elements[2], 6)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "[1, 2, 3][0]",
            1,
        ),
        (
            "[1, 2, 3][1]",
            2,
        ),
        (
            "[1, 2, 3][2]",
            3,
        ),
        (
            "let i = 0; [1][i];",
            1,
        ),
        (
            "[1, 2, 3][1 + 1];",
            3,
        ),
        (
            "let myArray = [1, 2, 3]; myArray[2];",
            3,
        ),
        (
            "let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];",
            6,
        ),
        (
            "let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]",
            2,
        ),
        (
            "[1, 2, 3][3]",
            None,
        ),
        (
            "[1, 2, 3][-1]",
            None,
        ),
    ],
)
def test_array_index_expressions(input: str, expected: Any) -> None:
    evaluated = _test_eval(input)
    if isinstance(expected, int):
        _test_integer_object(evaluated, expected)
    else:
        _test_null_object(evaluated)


def test_hash_literals() -> None:
    input = """
    let two = "two";
    {
        "one": 10 - 9,
        two: 1 + 1,
        "thr" + "ee": 6 / 2,
        4: 4,
        true: 5,
        false: 6
    }
    """

    evaluated = _test_eval(input)
    assert isinstance(evaluated, Hash)
    expected = {
        String("one").hash_key(): 1,
        String("two").hash_key(): 2,
        String("three").hash_key(): 3,
        Integer(4).hash_key(): 4,
        TRUE.hash_key(): 5,
        FALSE.hash_key(): 6,
    }
    assert len(evaluated.pairs) == len(expected)
    for expected_key, expected_value in expected.items():
        pair = evaluated.pairs[expected_key]
        assert isinstance(pair, HashPair)
        _test_integer_object(pair.value, expected_value)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            '{"foo": 5}["foo"]',
            5,
        ),
        (
            '{"foo": 5}["bar"]',
            None,
        ),
        (
            'let key = "foo"; {"foo": 5}[key]',
            5,
        ),
        (
            '{}["foo"]',
            None,
        ),
        (
            "{5: 5}[5]",
            5,
        ),
        (
            "{true: 5}[true]",
            5,
        ),
        (
            "{false: 5}[false]",
            5,
        ),
    ],
)
def test_hash_index_expressions(input: str, expected: Any) -> None:
    evaluated = _test_eval(input)
    if isinstance(expected, int):
        _test_integer_object(evaluated, expected)
    else:
        _test_null_object(evaluated)
