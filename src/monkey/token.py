from enum import Enum
from typing import NamedTuple


class TokenType(Enum):
    ILLEGAL = "ILLEGAL"
    EOF = "\x00"

    # Identifiers + literals
    IDENT = "IDENT"  # add, foobar, x, y, ...
    INT = "INT"  # 123123
    STRING = "STRING"  # "foobar"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"

    LT = "<"
    GT = ">"

    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"


class Token(NamedTuple):
    type: TokenType
    literal: str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.type}, '{self.literal}')"


STATIC_TOKENS: dict[str, Token] = {
    "=": Token(TokenType.ASSIGN, "="),
    "+": Token(TokenType.PLUS, "+"),
    "-": Token(TokenType.MINUS, "-"),
    "!": Token(TokenType.BANG, "!"),
    "*": Token(TokenType.ASTERISK, "*"),
    "/": Token(TokenType.SLASH, "/"),
    "<": Token(TokenType.LT, "<"),
    ">": Token(TokenType.GT, ">"),
    ",": Token(TokenType.COMMA, ","),
    ";": Token(TokenType.SEMICOLON, ";"),
    ":": Token(TokenType.COLON, ":"),
    "(": Token(TokenType.LPAREN, "("),
    ")": Token(TokenType.RPAREN, ")"),
    "{": Token(TokenType.LBRACE, "{"),
    "}": Token(TokenType.RBRACE, "}"),
    "[": Token(TokenType.LBRACKET, "["),
    "]": Token(TokenType.RBRACKET, "]"),
    "==": Token(TokenType.EQ, "=="),
    "!=": Token(TokenType.NOT_EQ, "!="),
    "\x00": Token(TokenType.EOF, "\x00"),
}


KEYWORDS: dict[str, Token] = {
    "fn": Token(TokenType.FUNCTION, "fn"),
    "let": Token(TokenType.LET, "let"),
    "true": Token(TokenType.TRUE, "true"),
    "false": Token(TokenType.FALSE, "false"),
    "if": Token(TokenType.IF, "if"),
    "else": Token(TokenType.ELSE, "else"),
    "return": Token(TokenType.RETURN, "return"),
}
