import sys

from app.tokenizer import Tokenizer

from app.parser import Parser

def stderr(*args, **kwargs):

    print(*args, file=sys.stderr, **kwargs)

def tokenize(file_contents: str):

    tokenizer = Tokenizer(contents=file_contents)

    line = 1

    valid = True

    while not tokenizer.terminated():

        token = tokenizer.next_token()

        if token.identifier == "ERROR":

            valid = False

            stderr(f"[line {line}] Error: {token.literal}")

            continue

        elif token.identifier == "NEWLINE":

            line += 1

        elif token.identifier == "COMMENT" or token.identifier == "WHITESPACE":

            continue

        else:

            print(f"{token.identifier} {token.lexeme} {token.literal}")

    print("EOF  null")

    if not valid:

        exit(65)

def parse(file_contents: str):

    parser = Parser(file_contents)

    print(parser.parse())

def main():

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    stderr("Logs from your program will appear here!")

    if len(sys.argv) < 3:

        stderr("Usage: ./your_program.sh tokenize <filename>")

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    with open(filename) as file:

        file_contents = file.read()

    match command:

        case "tokenize":

            tokenize(file_contents)

            return

        case "parse":

            parse(file_contents)

            return

        case _:

            stderr(f"Unknown command: {command}")

            exit(1)

if __name__ == "__main__":

    main()
