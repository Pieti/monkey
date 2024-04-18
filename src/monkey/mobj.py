from typing import Any, Callable

from monkey import ast
from monkey.environment import Environment


class HashKey:
    def __init__(self, monkey_type: str, value: Any):
        self.monkey_type = monkey_type
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashKey):
            return False
        return self.monkey_type == other.monkey_type and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.monkey_type, self.value))


class MonkeyObject:
    monkey_type: str = "OBJECT"

    def __init__(self, value: Any = None):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Hashable:
    def hash_key(self) -> HashKey:
        raise NotImplementedError()


class Boolean(MonkeyObject, Hashable):
    monkey_type: str = "BOOLEAN"

    def hash_key(self) -> HashKey:
        return HashKey(self.monkey_type, 0 if self.value else 1)

    def __init__(self, value: bool):
        super().__init__(value)


class Null(MonkeyObject):
    monkey_type: str = "NULL"

    def __init__(self):
        super().__init__(None)


class Integer(MonkeyObject, Hashable):
    monkey_type: str = "INTEGER"

    def hash_key(self) -> HashKey:
        return HashKey(self.monkey_type, self.value)

    def __init__(self, value: int):
        super().__init__(value)


class String(MonkeyObject, Hashable):
    monkey_type: str = "STRING"

    def hash_key(self) -> HashKey:
        return HashKey(self.monkey_type, hash(self.value))

    def __init__(self, value: str):
        super().__init__(value)


class Array(MonkeyObject):
    monkey_type: str = "ARRAY"

    def __init__(self, elements: list[MonkeyObject]):
        super().__init__(elements)
        self.elements = elements

    def __str__(self) -> str:
        return f"[{', '.join(str(e) for e in self.elements)}]"


class HashPair(MonkeyObject):
    def __init__(self, key: MonkeyObject, value: MonkeyObject):
        super().__init__()
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


class Hash(MonkeyObject):
    monkey_type: str = "HASH"

    def __init__(self, pairs: dict[HashKey, HashPair]):
        super().__init__(pairs)
        self.pairs = pairs

    def __str__(self) -> str:
        pairs = []
        for k, v in self.pairs.items():
            pairs.append(f"{k}: {v}")
        return f"{{{', '.join(pairs)}}}"


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
