import sys

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

    with open(filename) as file:

        file_contents = file.read()

    # Uncomment this block to pass the first stage

    line = 1

    error = False

    length = len(file_contents)

    i = 0

    reserved_words = [

        "and",

        "class",

        "else",

        "false",

        "for",

        "fun",

        "if",

        "nil",

        "or",

        "print",

        "return",

        "super",

        "this",

        "true",

        "var",

        "while",

    ]

    if file_contents:

        while i < length:

            c = file_contents[i]

            if c == "\n":

                line += 1

            elif c == " " or c == "\r" or c == "\t":

                pass

            elif c == "(":

                print("LEFT_PAREN ( null")

            elif c == ")":

                print("RIGHT_PAREN ) null")

            elif c == "{":

                print("LEFT_BRACE { null")

            elif c == "}":

                print("RIGHT_BRACE } null")

            elif c == ",":

                print("COMMA , null")

            elif c == ";":

                print("SEMICOLON ; null")

            elif c == ".":

                print("DOT . null")

            elif c == "-":

                print("MINUS - null")

            elif c == "+":

                print("PLUS + null")

            elif c == "*":

                print("STAR * null")

            elif c == "=":

                if i + 1 < length and file_contents[i + 1] == "=":

                    i += 1

                    print("EQUAL_EQUAL == null")

                else:

                    print("EQUAL = null")

            elif c == "!":

                if i + 1 < length and file_contents[i + 1] == "=":

                    i += 1

                    print("BANG_EQUAL != null")

                else:

                    print("BANG ! null")

            elif c == "<":

                if i + 1 < length and file_contents[i + 1] == "=":

                    i += 1

                    print("LESS_EQUAL <= null")

                else:

                    print("LESS < null")

            elif c == ">":

                if i + 1 < length and file_contents[i + 1] == "=":

                    i += 1

                    print("GREATER_EQUAL >= null")

                else:

                    print("GREATER > null")

            elif c == "/":

                if i + 1 < length and file_contents[i + 1] == "/":

                    while i < length and file_contents[i] != "\n":

                        i += 1

                    line += 1  # we got to /n

                else:

                    print("SLASH / null")

            elif c == '"':

                word = ""

                i += 1

                while i < length and file_contents[i] != '"':

                    word += file_contents[i]

                    i += 1

                if i == length:

                    error = True

                    print(f"[line {line}] Error: Unterminated string.", file=sys.stderr)

                else:

                    print(f'STRING "{word}" {word}')

            elif c.isalpha() or c == "_":

                word = c

                i += 1

                while i < length and (

                    file_contents[i].isalpha()

                    or file_contents[i].isdigit()

                    or file_contents[i] == "_"

                ):

                    word += file_contents[i]

                    i += 1

                #print(f"IDENTIFIER {word} null")

                if word in reserved_words:

                    print(f"{word.upper()} {word} null")

                else:

                    print(f"IDENTIFIER {word} null")

                i -= 1

            elif c.isdigit():

                only0 = True

                number = c

                i += 1

                while i < length and file_contents[i].isdigit():

                    number += file_contents[i]

                    i += 1

                if i < length and file_contents[i] == ".":

                    decimal_part = "."

                    i += 1

                    while i < length and file_contents[i].isdigit():

                        if file_contents[i] != "0":

                            only0 = False

                        decimal_part += file_contents[i]

                        i += 1

                    if (

                        len(decimal_part) > 1

                    ):  # If there are digits after the decimal point

                        number += decimal_part

                    else:

                        i -= 1

                literal_value = number if "." in number else number + ".0"

                if only0 and "." in number:

                    literal_value = number[: number.index(".") + 2]

                print(f"NUMBER {number} {literal_value}")

                i -= 1  # Adjust for the main loop's increment

            else:

                error = True

                print(

                    f"[line {line}] Error: Unexpected character: {c}", file=sys.stderr

                )

            i += 1

    print("EOF  null")

    if error:

        exit(65)

    exit(0)

if __name__ == "__main__":

    main()
