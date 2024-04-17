import sys
import typing

from monkey.lexer import Lexer
from monkey.parser import Parser

PROMPT: str = ">> "


def start(f: typing.IO = sys.stdout):
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            return

        try:
            lexer = Lexer(input=line)
            parser = Parser(lexer)
            program = parser.parse_program()
            f.write(f"{program}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
