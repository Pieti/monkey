from monkey import ast
from monkey.token import Token, TokenType


def test_string() -> None:
    program = ast.Program(
        statements=[
            ast.LetStatement(
                token=Token(TokenType.LET, "let"),
                name=ast.Identifier(
                    token=Token(TokenType.IDENT, "myVar"),
                    value="myVar",
                ),
                value=ast.Identifier(
                    token=Token(TokenType.IDENT, "anotherVar"),
                    value="anotherVar",
                ),
            )
        ]
    )

    assert str(program) == "let myVar = anotherVar;"
