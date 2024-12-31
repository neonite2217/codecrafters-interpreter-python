import sys

# match char:

#     case "(":

#         token.update({"LEFT_PAREN": "("});

#     case ")":

#         token.update({"RIGHT_PAREN": ")"});

#     case "{":

#         token.update({"LEFT_BRACE": "{"});

#     case "}":

#         token.update({"RIGHT_BRACE": "}"});

#     case "+":

#         token.update({"PLUS": "+"});

#     case "-":

#         token.update({"MINUS": "-"});

#     case "*":

#         token.update({"STAR": "*"});

#     case "/":

#         token.update({"SLASH": "/"});

#     case ".":

#         token.update({"DOT": "."});

#     case ",":

#         token.update({"COMMA": ","});

#     case ";":

#         token.update({"SEMICOLON":";"})

#     case _:

#         if not char.isspace():

#             error_.update({count:char})

#             count+=1

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

def main():

    lines_of_code = 1

    count = 0

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

    errorcode = 0

    error_message = []

    token = []

    for line_number, string in enumerate(file_contents.split("\n")):

        count_chr = 0

        while count_chr < len(string):

            if string[count_chr] in operators:

                match (string[count_chr]):

                    case "=":

                        if count_chr + 1 < len(string) and string[count_chr + 1] == "=":

                            token.append(f"EQUAL_EQUAL == null")

                            count_chr += 1

                        else:

                            token.append(

                                f"{operators[string[count_chr]]} {string[count_chr]} null"

                            )

                    case "!":

                        if count_chr + 1 < len(string) and string[count_chr + 1] == "=":

                            token.append(f"BANG_EQUAL != null")

                            count_chr += 1

                        else:

                            token.append(

                                f"{operators[string[count_chr]]} {string[count_chr]} null"

                            )

                    case ">":

                        if count_chr + 1 < len(string) and string[count_chr + 1] == "=":

                            token.append(f"GREATER_EQUAL >= null")

                            count_chr += 1

                        else:

                            token.append(

                                f"{operators[string[count_chr]]} {string[count_chr]} null"

                            )

                    case "<":

                        if count_chr + 1 < len(string) and string[count_chr + 1] == "=":

                            token.append(f"LESS_EQUAL <= null")

                            count_chr += 1

                        else:

                            token.append(

                                f"{operators[string[count_chr]]} {string[count_chr]} null"

                            )

                    case "/":

                        if count_chr + 1 < len(string) and string[count_chr + 1] == "/":

                            count_chr += len(string[2:]) + 1

                            pass

                        else:

                            token.append(

                                f"{operators[string[count_chr]]} {string[count_chr]} null"

                            )

                    case _:

                        token.append(

                            f"{operators[string[count_chr]]} {string[count_chr]} null"

                        )

            elif string[count_chr] in [" ", "\t"]:

                count_chr += 1

                continue

            else:

                errorcode = 65

                error_message.append(

                    f"[line {line_number + 1}] Error: Unexpected character: {string[count_chr]}"

                )

            count_chr += 1

    token.append("EOF  null")

    print("\n".join(error_message), file=sys.stderr)

    print("\n".join(token))

    exit(errorcode)

if __name__ == "__main__":

    main()
