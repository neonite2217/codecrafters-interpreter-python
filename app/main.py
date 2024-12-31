import sys

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

class Expr:

    class Unary:

        def __init__(self, operator, right):

            self.operator = operator

            self.right = right

    class Binary:

        def __init__(self, left, operator, right):

            self.left = left

            self.operator = operator

            self.right = right

    class Literals:

        def __init__(self, value):

            self.value = value

    class Grouping:

        def __init__(self, expression):

            self.expression = expression

    @staticmethod

    def printAST(expr):

        if isinstance(expr, Expr.Literals):

            return expr.value

        elif isinstance(expr, Expr.Grouping):

            return f"(group {Expr.printAST(expr.expression)})"

        elif isinstance(expr, Expr.Unary):

            return f"({expr.operator.lexeme} {Expr.printAST(expr.right)})"

        elif isinstance(expr, Expr.Binary):

            return f"({expr.operator.lexeme} {Expr.printAST(expr.left)} {Expr.printAST(expr.right)})"

        else:

            return expr

class Lox:

    had_error = False

    had_runtime_error = False

    @staticmethod

    def runtime_error(err):

        print(f"{err}\n[line {err.token.line}]", file=sys.stderr)

        Lox.had_runtime_error = True

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

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.index = 0

        self.errors = []

    def parse(self):

        return self.expression(), self.errors

    def expression(self):

        return self.equality()

    def equality(self):

        left = self.comparison()

        while self.match_type(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):

            operator = self.previous()

            right = self.comparison()

            left = Expr.Binary(left, operator, right)

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

            left = Expr.Binary(left, operator, right)

        return left

    def term(self):

        left = self.factor()

        while self.match_type(TokenType.PLUS, TokenType.MINUS):

            operator = self.previous()

            right = self.factor()

            left = Expr.Binary(left, operator, right)

        return left

    def factor(self):

        left = self.unary()

        while self.match_type(TokenType.SLASH, TokenType.STAR):

            operator = self.previous()

            right = self.unary()

            left = Expr.Binary(left, operator, right)

        return left

    def unary(self):

        while self.match_type(TokenType.BANG, TokenType.MINUS):

            operator = self.previous()

            return Expr.Unary(operator, self.unary())

        return self.primary()

    def primary(self):

        token = self.advance()

        match token.type:

            case TokenType.NIL:

                return Expr.Literals("nil")

            case TokenType.NUMBER:

                return Expr.Literals(token.literal)

            case TokenType.STRING:

                return Expr.Literals(token.literal)

            case TokenType.TRUE:

                return Expr.Literals("true")

            case TokenType.FALSE:

                return Expr.Literals("false")

            case TokenType.LEFT_PAREN:

                exp = self.expression()

                closing_paren = self.expect(TokenType.RIGHT_PAREN, f"Expected ).")

                if closing_paren:

                    return Expr.Grouping(exp)

            case TokenType.EOF:

                return

            case _:

                self.errors.append(f"[{token.line}]: Expected Expression")

    # def synchronize(self):

    #     self.advance();

    #     while not self.is_end():

    #         if self.previous().type == TokenType.SEMICOLON: return

    #         match self.peek().type:

    #             case TokenType.CLASS:

    #             case TokenType.FUN:

    #             case TokenType.VAR:

    #             case TokenType.FOR:

    #             case TokenType.IF:

    #             case TokenType.WHILE:

    #             case TokenType.PRINT:

    #             case TokenType.RETURN:

    #                 return

    #         self.advance();

    def expect(self, type, msg):

        token = self.advance()

        if token.type != type:

            self.errors.append(f"[{token.line}]: {msg}")

            return False

        else:

            return token

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

def to_string(value):

    if isinstance(value, float) and value.is_integer():

        return int(value)

    else:

        return str(value)

class RuntimeError(Exception):

    def __init__(self, token, msg):

        super().__init__(msg)

        self.token = token

def check_number_operand(operator: Token, operand: float):

    if not isinstance(operand, (float, int)):

        raise RuntimeError(operator, "Operand must be a number.")

def check_number_operands(operator: Token, left: any, right: any):

    if not (isinstance(left, (float, int)) and isinstance(right, (float, int))):

        raise RuntimeError(operator, "Operands must be a number.")

def is_string(value):

    return isinstance(value, str) and value not in ["true", "false", "nil"]

class Interpreter:

    def interpret(self, expr):

        try:

            print(to_string(self.evaluate(expr)))

        except RuntimeError as err:

            Lox.runtime_error(err)

    def evaluate(self, expr):

        if isinstance(expr, Expr.Literals):

            return self.eval_literals(expr)

        elif isinstance(expr, Expr.Grouping):

            return self.evaluate(expr.expression)

        elif isinstance(expr, Expr.Unary):

            return self.eval_unary(expr)

        elif isinstance(expr, Expr.Binary):

            return self.eval_binary(expr)

    def eval_literals(self, expr):

        if isinstance(expr.value, float) and expr.value.is_integer():

            return int(expr.value)

        return expr.value

    def eval_unary(self, expr):

        match expr.operator.type:

            case TokenType.MINUS:

                right = self.evaluate(expr.right)

                check_number_operand(expr.operator, right)

                return -1 * right

            case TokenType.BANG:

                value = self.evaluate(expr.right)

                if value == "false" or value == "nil":

                    return "true"

                return "false"

    def eval_binary(self, expr):

        left = self.evaluate(expr.left)

        right = self.evaluate(expr.right)

        match expr.operator.type:

            case TokenType.STAR:

                check_number_operands(expr.operator, left, right)

                return left * right

            case TokenType.SLASH:

                check_number_operands(expr.operator, left, right)

                return left / right

            case TokenType.PLUS:

                if (is_string(left) and is_string(right)) or (

                    isinstance(right, (float, int)) and isinstance(right, (float, int))

                ):

                    return left + right

                raise RuntimeError(

                    expr.operator, "Operands must be two numbers or two strings."

                )

            case TokenType.MINUS:

                check_number_operands(expr.operator, left, right)

                return left - right

            case TokenType.LESS:

                check_number_operands(expr.operator, left, right)

                return lox_boolean(left < right)

            case TokenType.LESS_EQUAL:

                check_number_operands(expr.operator, left, right)

                return lox_boolean(left <= right)

            case TokenType.GREATER:

                check_number_operands(expr.operator, left, right)

                return lox_boolean(left > right)

            case TokenType.GREATER_EQUAL:

                check_number_operands(expr.operator, left, right)

                return lox_boolean(left >= right)

            case TokenType.EQUAL_EQUAL:

                return lox_boolean(left == right)

            case TokenType.BANG_EQUAL:

                return lox_boolean(left != right)

def lox_boolean(bool):

    return "true" if bool else "false"

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    with open(filename) as file:

        file_contents = file.read()

    scanner = Scanner(file_contents)

    tokens, tk_errors = scanner.scan_tokens()

    if command == "tokenize":

        print("\n".join(tk_errors), file=sys.stderr)

        for token in tokens:

            print(str(token))

        exit(65 if len(tk_errors) > 0 else 0)

    elif command == "parse":

        print_error(tk_errors)

        parser = Parser(tokens)

        expression, p_errors = parser.parse()

        print_error(p_errors)

        print(Expr.printAST(expression))

        exit(0)

    elif command == "evaluate":

        print_error(tk_errors)

        parser = Parser(tokens)

        expression, p_errors = parser.parse()

        print_error(p_errors)

        interpreter = Interpreter()

        interpreter.interpret(expression)

        if Lox.had_runtime_error:

            exit(70)

        exit(0)

    else:

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

def print_error(errs):

    if errs:

        print("\n".join(errs), file=sys.stderr)

        exit(65)

if __name__ == "__main__":

    main()
