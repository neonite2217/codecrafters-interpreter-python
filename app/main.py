import sys

def scanning(lines):

    mapping = {

        "(": "LEFT_PAREN ( null",

        ")": "RIGHT_PAREN ) null",

        "{": "LEFT_BRACE { null",

        "}": "RIGHT_BRACE } null",

        "*": "STAR * null",

        ".": "DOT . null",

        ",": "COMMA , null",

        "+": "PLUS + null",

        "-": "MINUS - null",

        ";": "SEMICOLON ; null",

        "=": "EQUAL = null",

        "==": "EQUAL_EQUAL == null",

        "!": "BANG ! null",

        "!=": "BANG_EQUAL != null",

        "<": "LESS < null",

        "<=": "LESS_EQUAL <= null",

        ">": "GREATER > null",

        ">=": "GREATER_EQUAL >= null",

    }

    can_read_next = set("=!<>")

    has_error = 0

    read_two_tokens = False

    for line, contents in enumerate(lines):

        for i, c in enumerate(contents):

            if read_two_tokens:

                read_two_tokens = False

                continue

            try:

                if (
                    c in can_read_next

                    and i + 1 < len(contents)

                    and contents[i + 1] == "="

                ):

                    print(mapping[contents[i : i + 2]])

                    read_two_tokens = True

                else:

                    print(mapping[c])

            except KeyError:

                has_error = 65

                sys.stderr.write(f"[line {line+1}] Error: Unexpected character: {c}\n")

        else:

            print("EOF  null")

    exit(has_error)

def main():

     if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    if command != "tokenize":

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

    with open(filename) as file:

        file_contents = file.readlines()

    # Uncomment this block to pass the first stage

    if file_contents:

        scanning(file_contents)

    else:

        print(

            "EOF  null"

        )  # Placeholder, remove this line when implementing the scanner

if __name__ == "__main__":

    main()
