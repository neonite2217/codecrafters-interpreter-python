import enum

import sys

RET = 0

RET_LEXICAL_ERROR = 65

class Token:

    __slots__ = ("type", "repr")

    def __init__(self, type: str, repr: str) -> None:

        self.type = type

        self.repr = repr

    def __str__(self) -> str:

        return f"{self.type} {self.repr} null"

EOF_TOKEN = Token("EOF", "")

SINGLE_CHARACTER_TOKENS = [

    Token("LEFT_PAREN", "("),

    Token("RIGHT_PAREN", ")"),

    Token("LEFT_BRACE", "{"),

    Token("RIGHT_BRACE", "}"),

    Token("COMMA", ","),

    Token("DOT", "."),

    Token("MINUS", "-"),

    Token("PLUS", "+"),

    Token("SEMICOLON", ";"),

    Token("STAR", "*"),

    Token("DIV", "/"),

    Token("EQUAL", "="),

    Token("BANG", "!"),

    Token("LESS", "<"),

    Token("GREATER", ">"),

]

DOUBLE_CHARACTER_TOKENS = [

    Token("EQUAL_EQUAL", "=="),

    Token("BANG_EQUAL", "!="),

    Token("LESS_EQUAL", "<="),

    Token("GREATER_EQUAL", ">="),

]

class Lexer:

    def __init__(self, data: str) -> None:

        self._data = iter(data)

        self.corr = self.next = None

        self.readChar()

        self.readChar()

    def readChar(self) -> None:

        self.curr = self.next

        self.next = next(self._data, "\0")

    def __bool__(self) -> bool:

        return self.curr != "\0"

def scan(src: str) -> list[Token]:

    global RET

    result = []

    lexer = Lexer(src)

    lineno = 1

    single_char_tokens = {t.repr: t for t in SINGLE_CHARACTER_TOKENS}

    double_char_tokens = {t.repr: t for t in DOUBLE_CHARACTER_TOKENS}

    while lexer:

        c = lexer.curr

        n = lexer.next

        if token := double_char_tokens.get(c + n, None):

            result.append(token)

            lexer.readChar()

            lexer.readChar()

            continue

        if token := single_char_tokens.get(c, None):

            result.append(token)

            lexer.readChar()

            continue

        if c == "\n":

            lineno += 1

            lexer.readChar()

            continue

        print(f"[line {lineno}] Error: Unexpected character: {c}", file=sys.stderr)

        RET = RET_LEXICAL_ERROR

        lexer.readChar()

    result.append(EOF_TOKEN)

    return result

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    _, command, filename = sys.argv

    if command != "tokenize":

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

    with open(filename) as file:

        file_contents = file.read()

    tokens = scan(file_contents)

    print(*tokens, sep="\n")

    exit(RET)

if __name__ == "__main__":

    main()
