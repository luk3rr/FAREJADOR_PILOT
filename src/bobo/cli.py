# Filename: cli.py
# Created on: November 21, 2026
# Author: Lucas Araújo <araujolucas@dcc.ufmg.br>

"""Command line entry point: ``bobo add A B`` and ``bobo words TEXT``."""

import argparse
from collections.abc import Sequence

from bobo import calculator, text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bobo")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add two numbers")
    add.add_argument("a", type=float)
    add.add_argument("b", type=float)

    words = commands.add_parser("words", help="count the words of a text")
    words.add_argument("text")

    args = parser.parse_args(argv)
    if args.command == "add":
        print(calculator.add(args.a, args.b))
    else:
        print(text.count_words(args.text))
    return 0
