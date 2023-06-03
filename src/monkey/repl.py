from monkey.lexer import Lexer

PROMPT: str = ">> "


def start():
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            return

        lexer = Lexer(input=line)

        for token in lexer:
            print(token)
