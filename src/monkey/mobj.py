from typing import Any

from monkey import ast
from monkey.environment import Environment


class MonkeyObject:
    monkey_type: str = "OBJECT"

    def __init__(self, value: Any = None):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Integer(MonkeyObject):
    monkey_type: str = "INTEGER"

    def __init__(self, value: int):
        super().__init__(value)


class Boolean(MonkeyObject):
    monkey_type: str = "BOOLEAN"

    def __init__(self, value: bool):
        super().__init__(value)


class Null(MonkeyObject):
    monkey_type: str = "NULL"

    def __init__(self):
        super().__init__(None)


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


TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()
