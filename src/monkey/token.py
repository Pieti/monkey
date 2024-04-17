from enum import Enum
from typing import NamedTuple


class TokenType(Enum):
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    IDENT = "IDENT"
    INT = "INT"
    STRING = "STRING"

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

    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

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


ASSIGN = Token(TokenType.ASSIGN, "=")
PLUS = Token(TokenType.PLUS, "+")
MINUS = Token(TokenType.MINUS, "-")
BANG = Token(TokenType.BANG, "!")
ASTERISK = Token(TokenType.ASTERISK, "*")
SLASH = Token(TokenType.SLASH, "/")
LT = Token(TokenType.LT, "<")
GT = Token(TokenType.GT, ">")
COMMA = Token(TokenType.COMMA, ",")
SEMICOLON = Token(TokenType.SEMICOLON, ";")
COLON = Token(TokenType.COLON, ":")
LPAREN = Token(TokenType.LPAREN, "(")
RPAREN = Token(TokenType.RPAREN, ")")
LBRACE = Token(TokenType.LBRACE, "{")
RBRACE = Token(TokenType.RBRACE, "}")
LBRACKET = Token(TokenType.LBRACKET, "[")
RBRACKET = Token(TokenType.RBRACKET, "]")
EQ = Token(TokenType.EQ, "==")
NOT_EQ = Token(TokenType.NOT_EQ, "!=")
EOF = Token(TokenType.EOF, "\x00")

FUNCTION = Token(TokenType.FUNCTION, "fn")
LET = Token(TokenType.LET, "let")
TRUE = Token(TokenType.TRUE, "true")
FALSE = Token(TokenType.FALSE, "false")
IF = Token(TokenType.IF, "if")
ELSE = Token(TokenType.ELSE, "else")
RETURN = Token(TokenType.RETURN, "return")

STATIC_TOKENS: dict[str, Token] = {
    "=": ASSIGN,
    "+": PLUS,
    "-": MINUS,
    "!": BANG,
    "*": ASTERISK,
    "/": SLASH,
    "<": LT,
    ">": GT,
    ",": COMMA,
    ";": SEMICOLON,
    ":": COLON,
    "(": LPAREN,
    ")": RPAREN,
    "{": LBRACE,
    "}": RBRACE,
    "[": LBRACKET,
    "]": RBRACKET,
    "==": EQ,
    "!=": NOT_EQ,
    "\x00": EOF,
}


KEYWORDS: dict[str, Token] = {
    "fn": FUNCTION,
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "if": IF,
    "else": ELSE,
    "return": RETURN,
}
