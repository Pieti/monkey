from typing import Optional

from monkey.token import Token


class Node:
    def __init__(self, token: Token):
        self.token = token

    def __str__(self) -> str:
        return f"{self.token.literal}"


class Statement(Node):
    pass


class Expression(Node):
    pass


class Program(Node):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def __str__(self) -> str:
        return "".join(str(stmt) for stmt in self.statements)


class Identifier(Expression):
    def __init__(self, token: Token, value: str):
        super().__init__(token)
        self.value: str = value


class Boolean(Expression):
    def __init__(self, token: Token, value: bool):
        super().__init__(token)
        self.value: bool = value


class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int):
        super().__init__(token)
        self.value: int = value


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right: Expression):
        super().__init__(token)
        self.operator: str = operator
        self.right: Expression = right

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"


class InfixExpression(Expression):
    def __init__(
        self, token: Token, left: Expression, operator: str, right: Expression
    ):
        super().__init__(token)
        self.left: Expression = left
        self.operator: str = operator
        self.right: Expression = right

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


class IfExpression(Expression):
    def __init__(
        self,
        token: Token,
        condition: Expression,
        consequence: "BlockStatement",
        alternative: Optional["BlockStatement"] = None,
    ):
        super().__init__(token)
        self.condition: Expression = condition
        self.consequence: "BlockStatement" = consequence
        self.alternative: Optional["BlockStatement"] = alternative

    def __str__(self) -> str:
        s = f"if{self.condition} {self.consequence}"
        if self.alternative is not None:
            s += f"else {self.alternative}"
        return s


class FunctionLiteral(Expression):
    def __init__(
        self, token: Token, parameters: list[Identifier], body: "BlockStatement"
    ):
        super().__init__(token)
        self.parameters: list[Identifier] = parameters
        self.body: "BlockStatement" = body

    def __str__(self) -> str:
        return f"{self.token.literal}({', '.join(str(param) for param in self.parameters)}){self.body}"


class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression, arguments: list[Expression]):
        super().__init__(token)
        self.function: Expression = function
        self.arguments: list[Expression] = arguments

    def __str__(self) -> str:
        return f"{self.function}({', '.join(str(arg) for arg in self.arguments)})"


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str):
        super().__init__(token)
        self.value = value


class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression]):
        super().__init__(token)
        self.elements: list[Expression] = elements

    def __str__(self) -> str:
        return f"[{', '.join(str(elem) for elem in self.elements)}]"


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression, index: Expression):
        super().__init__(token)
        self.left: Expression = left
        self.index: Expression = index

    def __str__(self) -> str:
        return f"({self.left}[{self.index}])"


class HashLiteral(Expression):
    def __init__(self, token: Token, pairs: dict[Expression, Expression]):
        super().__init__(token)
        self.pairs: dict[Expression, Expression] = pairs

    def __str__(self) -> str:
        pairs = []
        for k, v in self.pairs.items():
            pairs.append(": ".join([str(k), str(v)]))

        return f"{{{', '.join(pairs)}}}"


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, value: Expression):
        super().__init__(token)
        self.name: Identifier = name
        self.value: Expression = value

    def __str__(self) -> str:
        return f"{self.token.literal} {self.name} = {self.value};"


class ReturnStatement(Statement):
    def __init__(self, token: Token, value: Expression):
        super().__init__(token)
        self.value: Expression = value

    def __str__(self) -> str:
        s = f"{self.token.literal} "
        if self.value is not None:
            s += f"{self.value}"
        return s + ";"


class ExpressionStatement(Statement):
    def __init__(self, token: Token, expression: Expression):
        super().__init__(token)
        self.expression: Expression = expression

    def __str__(self) -> str:
        return f"{self.expression}"


class BlockStatement(Statement):
    def __init__(self, token: Token, statements: list[Statement]):
        super().__init__(token)
        self.statements: list[Statement] = statements

    def __str__(self) -> str:
        return "\n".join(str(stmt) for stmt in self.statements)
