import sys

from . import error

from .scanner import Scanner

from .parser import Parser

from .ast_printer import AstPrinter

from .interpreter import Interpreter

interpreter = Interpreter()

def main() -> None:

    if len(sys.argv) == 1:  # run interactive interpreter

        run_prompt()

    elif len(sys.argv) > 3:

        print("Too many args", sys.stderr)

    else:  # run file

        if len(sys.argv) == 3:  # command provided

            command = sys.argv[1]

            filename = sys.argv[2]

        else:

            filename = sys.argv[1]

            command = ""

        if command not in ["", "tokenize", "parse", "evaluate", "run"]:

            print(f"Unknown command: {command}", file=sys.stderr)

            exit(64)

        run_file(filename, command)

def run_file(filename: str, command: str = "") -> None:

    with open(filename) as file:

        file_contents = file.read()

    match command:

        case "run":

            run(file_contents)

        case "evaluate":

            run_eval(file_contents)

        case "parse":

            run_parse(file_contents)

        case "tokenize":

            run_tokenize(file_contents)

            # print(f"[SCANNER] done. Error: {error.hadError}", file=sys.stderr)

        case _:

            run(file_contents)

    if error.hadError:

        exit(65)

    if error.hadRuntimeError:

        exit(70)

def run_prompt() -> None:

    while True:

        try:

            prompt = input("> ")

            run(prompt)

            error.hadError = False

        except EOFError:

            break

def run_tokenize(source: str) -> None:

    scanner = Scanner(source)

    tokens = scanner.scanTokens()

    for token in tokens:

        print(token)

def run_parse(source: str) -> None:

    scanner = Scanner(source)

    tokens = scanner.scanTokens()

    parser = Parser(tokens)

    expression = parser.parse_expr()

    if error.hadError or expression is None:

        return

    print(AstPrinter({}).print(expression))

def run_eval(source: str) -> None:

    scanner = Scanner(source)

    tokens = scanner.scanTokens()

    parser = Parser(tokens)

    expression = parser.parse_expr()

    if error.hadError or expression is None:

        return

    interpreter.interpret_expr(expression)

def run(source: str) -> None:

    scanner = Scanner(source)

    tokens = scanner.scanTokens()

    parser = Parser(tokens)

    statements = parser.parse()

    # for i, s in enumerate(statements):

    #     print(f"[Stmt {i}] {printer.print(s)}")

    if error.hadError:

        return

    interpreter.interpret(statements)

main()
