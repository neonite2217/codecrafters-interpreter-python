import sys

import os

def match_keyword(char, line_number=1):

    match char:

        case "(":

            return f"LEFT_PAREN {char} null", True

        case ")":

            return f"RIGHT_PAREN {char} null", True

        case "{":

            return f"LEFT_BRACE {char} null", True

        case "}":

            return f"RIGHT_BRACE {char} null", True

        case ",":

            return f"COMMA {char} null", True

        case ".":

            return f"DOT {char} null", True

        case ";":

            return f"SEMICOLON {char} null", True

        case "+":

            return f"PLUS {char} null", True

        case "*":

            return f"STAR {char} null", True

        case "-":

            return f"MINUS {char} null", True

        case "":

            return f"EOF {char} null", True

        case "==":

            return f"EQUAL_EQUAL {char} null", True

        case "!=":

            return f"BANG_EQUAL {char} null", True

        case "<":

            return f"LESS {char} null", True

        case "<=":

            return f"LESS_EQUAL {char} null", True

        case ">":

            return f"GREATER {char} null", True

        case ">=":

            return f"GREATER_EQUAL {char} null", True

        case "!":

            return f"BANG {char} null", True

        case "=":

            return f"EQUAL {char} null", True

        case "/":

            return f"SLASH {char} null", True

        case _:

            return f"[line {line_number}] Error: Unexpected character: {char}", False

def print_token(return_str, not_error=True):

    if not_error:

        print(return_str)

        return None

    else:

        print(return_str, file=sys.stderr)

        return 65

def main():

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    # print("Logs from your program will appear here!", file=sys.stderr)

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    if command != "tokenize":

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

    if not os.path.exists(filename):

        file_contents = filename

    else:

        with open(filename) as file:

            file_contents = file.read()

    # Uncomment this block to pass the first stage

    if file_contents:

        res = None

        error_code = None

        i = 0

        # print(file_contents)

        while i < len(file_contents):

            char = file_contents[i]

            if char in ["=", "!"]:

                # print(f"LEN FILE CONTENTS {len(file_contents)} and i+1 {i+1}")

                if len(file_contents) > i + 1 and file_contents[i + 1] == "=":

                    res = print_token(

                        *match_keyword(f"{file_contents[i]}{file_contents[i+1]}")

                    )

                    i += 1

                else:

                    res = print_token(*match_keyword(char))

            elif char in ["<", ">"]:

                if len(file_contents) > i + 1 and file_contents[i + 1] == "=":

                    res = print_token(

                        *match_keyword(f"{file_contents[i]}{file_contents[i+1]}")

                    )

                    i += 1

                else:

                    res = print_token(*match_keyword(char))

            elif char in ["/"]:

                if len(file_contents) > i + 1 and file_contents[i + 1] == "/":

                    while i < len(file_contents) and file_contents[i] != "\n":

                        i += 1

                else:

                    res = print_token(*match_keyword(char))

            else:

                res = print_token(*match_keyword(char))

            i += 1

            error_code = error_code if error_code is not None else res

        print("EOF  null")

        if error_code:

            exit(error_code)

        else:

            exit(0)

    else:

        print(

            "EOF  null"

        )  # Placeholder, remove this line when implementing the scanner

if __name__ == "__main__":

    main()
