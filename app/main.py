import sys

from .parser import Parser

from .scanner import Scanner

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    with open(filename) as file:

        file_contents = file.read()

    scanner = Scanner(file_contents)

    scanner.scan()

    match command:

        case "tokenize":

            scanner.print_tokens()

            if scanner.has_errors():

                scanner.print_errors()

                sys.exit(65)

        case "parse":

            if scanner.has_errors():

                scanner.print_errors()

                sys.exit(65)

            parser = Parser(scanner.tokens)

            expr = parser.expression()

            if parser.has_errors():

                parser.print_errors()

                sys.exit(65)

            print(expr)

        case _:

            print(f"Unknown command: {command}", file=sys.stderr)

            exit(1)

if __name__ == "__main__":

    main()
