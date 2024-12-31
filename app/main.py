import sys

operators = {

    "+": "PLUS",

    "-": "MINUS",

    "*": "STAR",

    "/": "SLASH",

    "(": "LEFT_PAREN",

    ")": "RIGHT_PAREN",

    "{": "LEFT_BRACE",

    "}": "RIGHT_BRACE",

    ",": "COMMA",

    ";": "SEMICOLON",

    ".": "DOT",

    "=": "EQUAL",

    "!": "BANG",

    ">": "GREATER",

    "<": "LESS",

}

def append_token(token, string, count_chr, operator, dual_op=None):

    if dual_op and count_chr + 1 < len(string) and string[count_chr + 1] == "=":

        token.append(f"{operator}_EQUAL {dual_op} null")

        return count_chr + 1

    token.append(f"{operators[string[count_chr]]} {string[count_chr]} null")

    return count_chr

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command, filename = sys.argv[1], sys.argv[2]

    if command != "tokenize":

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

    with open(filename) as file:

        file_contents = file.read()

    errorcode, error_message, token = 0, [], []

    for line_number, string in enumerate(file_contents.split("\n")):

        count_chr = 0

        while count_chr < len(string):

            if string[count_chr] in operators:

                if string[count_chr] == "=":

                    count_chr = append_token(token, string, count_chr, "EQUAL", "==")

                elif string[count_chr] == "!":

                    count_chr = append_token(token, string, count_chr, "BANG", "!=")

                elif string[count_chr] == ">":

                    count_chr = append_token(token, string, count_chr, "GREATER", ">=")

                elif string[count_chr] == "<":

                    count_chr = append_token(token, string, count_chr, "LESS", "<=")

                elif string[count_chr] == "/":

                    if count_chr + 1 < len(string) and string[count_chr + 1] == "/":

                        break

                    count_chr = append_token(token, string, count_chr, "SLASH")

                else:

                    token.append(

                        f"{operators[string[count_chr]]} {string[count_chr]} null"

                    )

            elif string[count_chr] in [" ", "\t"]:

                line_number += 1

                pass

            else:

                errorcode = 65

                error_message.append(

                    f"[line {line_number + 1}] Error: Unexpected character: {string[count_chr]}"

                )

            count_chr += 1

    token.append("EOF  null")

    if error_message:

        print("\n".join(error_message), file=sys.stderr)

    print("\n".join(token))

    exit(errorcode)

if __name__ == "__main__":

    main()
