import sys

import re

from enum import Enum

TokenType = Enum(

    "TokenType",

    [

        # Single-character tokens.

        "LEFT_PAREN",

        "RIGHT_PAREN",

        "LEFT_BRACE",

        "RIGHT_BRACE",

        "COMMA",

        "DOT",

        "MINUS",

        "PLUS",

        "SEMICOLON",

        "SLASH",

        "STAR",

        # One or two character tokens.

        "BANG",

        "BANG_EQUAL",

        "EQUAL",

        "EQUAL_EQUAL",

        "GREATER",

        "GREATER_EQUAL",

        "LESS",

        "LESS_EQUAL",

        # Literals.

        "IDENTIFIER",

        "STRING",

        "NUMBER",

        # Keywords.

        "AND",

        "CLASS",

        "ELSE",

        "FALSE",

        "FUN",

        "FOR",

        "IF",

        "NIL",

        "OR",

        "PRINT",

        "RETURN",

        "SUPER",

        "THIS",

        "TRUE",

        "VAR",

        "WHILE",

        "EOF",

    ],

)

reserved_keywords = {

    "and": TokenType.AND,

    "class": TokenType.CLASS,

    "else": TokenType.ELSE,

    "false": TokenType.FALSE,

    "for": TokenType.FOR,

    "fun": TokenType.FUN,

    "if": TokenType.IF,

    "nil": TokenType.NIL,

    "or": TokenType.OR,

    "print": TokenType.PRINT,

    "return": TokenType.RETURN,

    "super": TokenType.SUPER,

    "this": TokenType.THIS,

    "true": TokenType.TRUE,

    "var": TokenType.VAR,

    "while": TokenType.WHILE,

}

class Token:

    def __init__(self, type, lexeme, literal, line):

        self.type = type

        self.lexeme = lexeme

        self.literal = literal

        self.line = line

    def __str__(self):

        literal_str = "null" if self.literal is None else str(self.literal)

        return f"{self.type.name} {self.lexeme} {literal_str}"

class Scanner:

    def __init__(self, source):

        self.source = source

        self.length = len(source)

        self.tokens = []

        self.errors = []

        self.start = 0

        self.index = 0

        self.line = 1

    def scan_tokens(self):

        while self.index < self.length:

            self.start = self.index

            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens, self.errors

    def scan_token(self):

        char = self.advance()

        match char:

            case "\n":

                self.line += 1

            case "(":

                self.add_token(TokenType.LEFT_PAREN)

            case ")":

                self.add_token(TokenType.RIGHT_PAREN)

            case "{":

                self.add_token(TokenType.LEFT_BRACE)

            case "}":

                self.add_token(TokenType.RIGHT_BRACE)

            case ",":

                self.add_token(TokenType.COMMA)

            case ".":

                self.add_token(TokenType.DOT)

            case "-":

                self.add_token(TokenType.MINUS)

            case "+":

                self.add_token(TokenType.PLUS)

            case ";":

                self.add_token(TokenType.SEMICOLON)

            case "*":

                self.add_token(TokenType.STAR)

            case "!":

                self.add_token(

                    TokenType.BANG_EQUAL if self.is_next("=") else TokenType.BANG

                )

            case "=":

                self.add_token(

                    TokenType.EQUAL_EQUAL if self.is_next("=") else TokenType.EQUAL

                )

            case "<":

                self.add_token(

                    TokenType.LESS_EQUAL if self.is_next("=") else TokenType.LESS

                )

            case ">":

                self.add_token(

                    TokenType.GREATER_EQUAL if self.is_next("=") else TokenType.GREATER

                )

            case "/":

                if self.is_next("/"):

                    while self.peek() != "\n" and not self.is_end():

                        self.advance()

                else:

                    self.add_token(TokenType.SLASH)

            case '"':

                self.string()

            case _:

                if char.isspace():

                    pass

                elif char.isnumeric():

                    self.number()

                elif char.isalpha() or char == "_":

                    self.identifier()

                else:

                    self.errors.append(

                        f"[line {self.line}] Error: Unexpected character: {char}"

                    )

    def add_token(self, type, literal=None):

        lexeme = self.source[self.start : self.index]

        self.tokens.append(Token(type, lexeme, literal, self.line))

    def advance(self):

        self.index += 1

        return self.source[self.index - 1]

    def is_end(self):

        return self.index >= self.length

    def is_next(self, expected):

        if self.is_end() or self.source[self.index] != expected:

            return False

        self.index += 1

        return True

    def peek(self):

        if self.is_end():

            return "\0"

        return self.source[self.index]

    def peek_next(self):

        if self.index + 1 >= self.length:

            return "\0"

        return self.source[self.index + 1]

    def string(self):

        while self.peek() != '"' and not self.is_end():

            if self.peek() == "\n":

                self.line += 1

            self.advance()

        if self.is_end():

            self.errors.append(f"[line {self.line}] Error: Unterminated string.")

            return

        self.advance()

        value = self.source[self.start + 1 : self.index - 1]

        self.add_token(TokenType.STRING, value)

    def number(self):

        while self.peek().isnumeric():

            self.advance()

        if self.peek() == "." and self.peek_next().isnumeric():

            self.advance()

        while self.peek().isnumeric():

            self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.index]))

    def identifier(self):

        while self.peek().isalnum() or self.peek() == "_":

            self.advance()

        text = self.source[self.start : self.index]

        type = (

            reserved_keywords[text]

            if text in reserved_keywords

            else TokenType.IDENTIFIER

        )

        self.add_token(type)

# Equality	== !=	Left

# Comparison	> >= < <=	Left

# Term	- +	Left

# Factor	/ *	Left

# Unary	! -	Right

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.index = 0

        self.errors = []

    def parse(self):

        while not self.is_end():

            exp = self.expression()

            print(exp)

        return self.errors

    def expression(self):

        return self.equality()

    def equality(self):

        left = self.comparison()

        while self.match_type(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):

            operator = self.previous()

            right = self.comparison()

            left = BinaryExp(left, operator, right)

        return left

    def comparison(self):

        left = self.term()

        while self.match_type(

            TokenType.LESS_EQUAL,

            TokenType.LESS,

            TokenType.GREATER,

            TokenType.GREATER_EQUAL,

        ):

            operator = self.previous()

            right = self.term()

            left = BinaryExp(left, operator, right)

        return left

    def term(self):

        left = self.factor()

        while self.match_type(TokenType.PLUS, TokenType.MINUS):

            operator = self.previous()

            right = self.factor()

            left = BinaryExp(left, operator, right)

        return left

    def factor(self):

        left = self.unary()

        while self.match_type(TokenType.SLASH, TokenType.STAR):

            operator = self.previous()

            right = self.unary()

            left = BinaryExp(left, operator, right)

        return left

    def unary(self):

        while self.match_type(TokenType.BANG, TokenType.MINUS):

            op = self.previous()

            return f"({op.lexeme} {self.unary()})"

        return self.primary()

    def primary(self):

        token = self.advance()

        match token.type:

            case TokenType.NIL:

                return "nil"

            case TokenType.NUMBER:

                return token.literal

            case TokenType.STRING:

                return token.literal

            case TokenType.TRUE:

                return "true"

            case TokenType.FALSE:

                return "false"

            case TokenType.LEFT_PAREN:

                exp = self.expression()

                self.expect(TokenType.RIGHT_PAREN, f"Expected )")

                return f"(group {exp})"

            case _:

                return ""

    def expect(self, type, msg):

        if self.advance().type != type:

            self.errors.append(msg)

            return False

        else:

            return True

    def advance(self):

        token = self.peek()

        self.index += 1

        return token

    def peek(self):

        if self.is_end():

            return ""

        return self.tokens[self.index]

    def peek_type(self):

        if self.is_end():

            return ""

        return self.peek().type

    def peek_next(self):

        return self.tokens[self.index + 1]

    def previous(self):

        return self.tokens[self.index - 1]

    def match_type(self, *types):

        if self.peek_type() in types:

            self.advance()

            return True

        else:

            return False

    def is_end(self):

        return self.index >= len(self.tokens)

#  Helper functions

def BinaryExp(left, op, right):

    return f"({op.lexeme} {left} {right})"

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    with open(filename) as file:

        file_contents = file.read()

    scanner = Scanner(file_contents)

    tokens, errors = scanner.scan_tokens()

    if command == "tokenize":

        print("\n".join(errors), file=sys.stderr)

        for token in tokens:

            print(str(token))

        exit(65 if len(errors) > 0 else 0)

    elif command == "parse":

        parser = Parser(tokens)

        errors = parser.parse()

        print("\n".join(errors), file=sys.stderr)

        exit(65 if len(errors) > 0 else 0)

    else:

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

if __name__ == "__main__":

    main()
