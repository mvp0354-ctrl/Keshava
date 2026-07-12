# main.py
#
# Entry point for running a Keshava (.msm) program.
#
# Usage:
#   python main.py sample.msm

import sys

from lexer import lexer
from parser import Parser, ParserError
from interpreter import Interpreter, msmRuntimeError


def run_file(path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = lexer(code)
    except RuntimeError as e:
        print(f"Lexer error: {e}")
        sys.exit(1)

    try:
        ast = Parser(tokens).parse()
    except ParserError as e:
        print(f"Syntax error: {e}")
        sys.exit(1)

    interpreter = Interpreter()
    try:
        interpreter.run(ast)
    except msmRuntimeError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.msm>")
        sys.exit(1)

    run_file(sys.argv[1])


if __name__ == "__main__":
    main()
