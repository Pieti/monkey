import sys
import typing

from monkey.environment import Environment
from monkey.evaluator import monkey_eval
from monkey.lexer import Lexer
from monkey.parser import Parser

PROMPT: str = ">> "


def start(f: typing.IO = sys.stdout):
    env = Environment()
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            return

        try:
            lexer = Lexer(input=line)
            parser = Parser(lexer)
            program = parser.parse_program()
        except Exception as e:
            f.write(f"Error: {e}\n")
            continue

        evaluated = monkey_eval(program, env)
        f.write(f"{evaluated}\n")
