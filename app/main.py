import sys

def main():

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    print("Logs from your program will appear here!", file=sys.stderr)

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

    exit_code = 0

    # Uncomment this block to pass the first stage

    toks = []

    errs = []

    if file_contents:

        line_no = 1

        ptr = 0

        while ptr < len(file_contents):

            ch = file_contents[ptr]

            ch_name = ""

            if ch == "(":

                ch_name = "LEFT_PAREN"

            elif ch == ")":

                ch_name = "RIGHT_PAREN"

            elif ch == "{":

                ch_name = "LEFT_BRACE"

            elif ch == "}":

                ch_name = "RIGHT_BRACE"

            elif ch == ",":

                ch_name = "COMMA"

            elif ch == ".":

                ch_name = "DOT"

            elif ch == "+":

                ch_name = "PLUS"

            elif ch == "-":

                ch_name = "MINUS"

            elif ch == ";":

                ch_name = "SEMICOLON"

            elif ch == "*":

                ch_name = "STAR"

            elif ch == "\n":

                line_no += 1

                continue

            elif ch == "=":

                if ptr < len(file_contents) - 1 and file_contents[ptr + 1] == "=":

                    ch_name = "EQUAL_EQUAL"

                    ch = "=="

                else:

                    ch_name = "EQUAL"

            else:

                errs.append(f"[line {line_no}] Error: Unexpected character: {ch}")

                exit_code = 65

                ptr += 1

                continue

            ptr += len(ch)

            toks.append(f"{ch_name} {ch} null")

        toks.append(

            "EOF  null"

        )  # Placeholder, remove this line when implementing the scanner

        print("\n".join(errs), file=sys.stderr)

        print("\n".join(toks))

    else:

        print(

            "EOF  null"

        )  # Placeholder, remove this line when implementing the scanner

    exit(exit_code)

if __name__ == "__main__":

    main()
