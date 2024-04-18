from typing import Any, Callable

from monkey import ast
from monkey.environment import Environment


class MonkeyObject:
    monkey_type: str = "OBJECT"

    def __init__(self, value: Any = None):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Boolean(MonkeyObject):
    monkey_type: str = "BOOLEAN"

    def __init__(self, value: bool):
        super().__init__(value)


class Null(MonkeyObject):
    monkey_type: str = "NULL"

    def __init__(self):
        super().__init__(None)


class Integer(MonkeyObject):
    monkey_type: str = "INTEGER"

    def __init__(self, value: int):
        super().__init__(value)


class String(MonkeyObject):
    monkey_type: str = "STRING"

    def __init__(self, value: str):
        super().__init__(value)


class Array(MonkeyObject):
    monkey_type: str = "ARRAY"

    def __init__(self, elements: list[MonkeyObject]):
        super().__init__(elements)
        self.elements = elements

    def __str__(self) -> str:
        return f"[{', '.join(str(e) for e in self.elements)}]"


class ReturnValue(MonkeyObject):
    monkey_type: str = "RETURN_VALUE"

    def __init__(self, value: MonkeyObject):
        super().__init__(value)


class Error(MonkeyObject):
    monkey_type: str = "ERROR"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Error: {self.value}"


class Function(MonkeyObject):
    monkey_type: str = "FUNCTION"

    def __init__(
        self,
        parameters: list[ast.Identifier],
        body: ast.BlockStatement,
        env: Environment,
    ):
        super().__init__()
        self.parameters = parameters
        self.body = body
        self.env = env


class Builtin(MonkeyObject):
    monkey_type: str = "BUILTIN"

    def __init__(self, fn: Callable):
        super().__init__(fn)
        self.fn = fn

    def __call__(self, *args: MonkeyObject) -> MonkeyObject:
        return self.fn(*args)

    def __str__(self) -> str:
        return "builtin function"


TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()
