import sys

from .token import Token

class Expression:

    def __str__(self):

        pass

class UnaryExpression(Expression):

    def __init__(self, operator: Token, expression: Expression):

        self.operator = operator

        self.expression = expression

    def __str__(self):

        return f"({self.operator.lexeme} {self.expression})"

class GroupExpression(Expression):

    def __init__(self, expression: Expression):

        self.expression = expression

    def __str__(self):

        return f"(group {self.expression})"

class LiteralExpression(Expression):

    def __init__(self, value: str | bool | float | None):

        self.value = value

    def __str__(self):

        return str(self.value)

class BinaryExpression(Expression):

    def __init__(self, left: Expression, operator: Token, right: Expression):

        self.left = left

        self.operator = operator

        self.right = right

        self.expression: str

    def __str__(self):

        return f"({self.operator.lexeme} {self.left} {self.right})"

class Parser:

    def __init__(self, tokens: list[Token]):

        self.tokens: list[Token] = tokens

        self.current = 0

        self.errors: list[str] = []

    def has_errors(self) -> bool:

        return len(self.errors) > 0

    def print_errors(self):

        for error in self.errors:

            print(error, file=sys.stderr)

    def report(self, message: str):

        self.errors.append(f"Error: {message}")

    def is_at_end(self) -> bool:

        return self.peek().type == "EOF"

    def advance(self) -> Token:

        if not self.is_at_end():

            self.current += 1

        return self.previous()

    def peek(self) -> Token:

        return self.tokens[self.current]

    def previous(self):

        return self.tokens[self.current - 1]

    def peek_next(self) -> Token | None:

        if self.current + 1 >= len(self.tokens):

            return None

        return self.tokens[self.current + 1]

    def check(self, token_type: str):

        if self.is_at_end():

            return False

        return self.peek().type == token_type

    def print_expression(self):

        if self.expression is None:

            print("")

        else:

            print(self.expression)

    def match(self, token_types: list[str]):

        for token_type in token_types:

            if self.check(token_type):

                self.advance()

                return True

        return False

    def consume(self, token_type: str, message: str):

        if self.check(token_type):

            return self.advance()

        self.report(message)

    def primary(self):

        if self.match(["FALSE"]):

            return LiteralExpression("false")

        if self.match(["TRUE"]):

            return LiteralExpression("true")

        if self.match(["NIL"]):

            return LiteralExpression("nil")

        if self.match(["NUMBER", "STRING"]):

            return LiteralExpression(self.previous().literal)

        if self.match(["LEFT_PAREN"]):

            expr = self.expression()

            if expr is None:

                self.report("Empty group")

                return

            self.consume("RIGHT_PAREN", "Expect ')' after expression.")

            return GroupExpression(expr)

    def unary(self):

        if self.match(["BANG", "MINUS"]):

            operator = self.previous()

            right = self.unary()

            return UnaryExpression(operator, right)

        return self.primary()

    def factor(self):

        expr = self.unary()

        while self.match(["SLASH", "STAR"]):

            operator = self.previous()

            right = self.unary()

            expr = BinaryExpression(expr, operator, right)

        return expr

    def term(self):

        expr = self.factor()

        while self.match(["MINUS", "PLUS"]):

            operator = self.previous()

            right = self.factor()

            if right is None:

                self.report("Empty group")

                return

            expr = BinaryExpression(expr, operator, right)

        return expr

    def comparison(self) -> Expression:

        expr = self.term()

        while self.match(["GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"]):

            operator = self.previous()

            right = self.term()

            expr = BinaryExpression(expr, operator, right)

        return expr

    def equality(self) -> Expression:

        expr = self.comparison()

        while self.match(["BANG_EQUAL", "EQUAL_EQUAL"]):

            operator = self.previous()

            right = self.comparison()

            expr = BinaryExpression(expr, operator, right)

        return expr

    def expression(self) -> Expression:

        return self.equality()
