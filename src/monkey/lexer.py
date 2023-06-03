from monkey.token import KEYWORDS, STATIC_TOKENS, Token, TokenType


def is_letter(ch: str) -> bool:
    return ch.isalpha() or ch == "_"


def is_number(ch: str) -> bool:
    return ch.isdigit()


class Lexer:
    def __init__(self, input: str):
        self.input: str = input
        self.position: int = 0
        self.last_position = len(self.input)
        self.read_position: int = 0
        self.ch: str = ""
        self.read_char()

    def next_token(self) -> Token:
        self.skip_whitespace()

        literal = self.ch
        if literal in {"=", "!"}:
            if self.peek_char() == "=":
                self.read_char()
                literal += self.ch

        if token := STATIC_TOKENS.get(literal):
            self.read_char()
            return token

        if is_letter(literal):
            ident = self.read_identifier()
            return KEYWORDS.get(ident, Token(TokenType.IDENT, ident))

        if is_number(literal):
            return Token(TokenType.INT, self.read_number())

        if literal == '"':
            token = Token(TokenType.STRING, self.read_string())
            self.read_char()
            return token

        return Token(TokenType.ILLEGAL, literal)

    def read_char(self) -> None:
        self.ch = self.peek_char()
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        if self.read_position >= self.last_position:
            return "\x00"
        else:
            return self.input[self.read_position]

    def skip_whitespace(self) -> None:
        while self.ch in ["", " ", "\t", "\n", "\r"]:
            self.read_char()

    def read_identifier(self) -> str:
        position = self.position

        while is_letter(self.ch):
            self.read_char()
        return self.input[position : self.position]

    def read_number(self) -> str:
        position = self.position

        while is_number(self.ch):
            self.read_char()
        return self.input[position : self.position]

    def read_string(self) -> str:
        position = self.position + 1
        self.read_char()
        while self.ch not in {'"', "\x00"}:
            self.read_char()
        return self.input[position : self.position]

    def __iter__(self):
        while self.ch != "\x00":
            yield self.next_token()
