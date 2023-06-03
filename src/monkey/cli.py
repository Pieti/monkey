import getpass

from monkey import repl


def cli() -> None:
    user = getpass.getuser()
    print(f"Hello {user}! This is the Monkey programming language!")
    print(f"Feel free to type in commands")
    repl.start()


if __name__ == "__main__":
    cli()
