from abc import ABC, abstractmethod
import sys


class Token:
    def __init__(self, type, lexeme, literal):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __repr__(self) -> str:
        return f"{self.type} {self.lexeme} {'null' if self.literal is None else self.literal}"


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        print(f"Undefined variable '{name}'", file=sys.stderr)
        exit(70)

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            print(f"Undefined variable '{name}'", file=sys.stderr)
            exit(70)


class Scanner:
    def __init__(self, source_code) -> None:
        self.source_code = source_code
        self.current = 0
        self.line = 1
        self.had_error = False

    def scan(self):
        tokens = []
        while self.current < len(self.source_code):
            self.current += 1
            char = self.source_code[self.current - 1]
            # Scanner logic here ...
            # Code for scanning tokens (left out for brevity)
            # (same as your original Scanner class)

        tokens.append(Token("EOF", "", None))
        return tokens, self.had_error


class Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, env):
        pass


class LiteralExpression(Expression):
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.value is True: return "true"
        if self.value is False: return "false"
        if self.value is None: return "nil"
        return f"{self.value}"

    def evaluate(self, env):
        return self.value


class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, env):
        return env.get(self.name)

    def __str__(self) -> str:
        return f"(identifier {self.name})"


class UnaryExpression(Expression):
    def __init__(self, operator: Token, expression: Expression) -> None:
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.expression})"

    def evaluate(self, env):
        value = self.expression.evaluate(env)
        if self.operator.type == "MINUS":
            if not isinstance(value, float):
                print(f"Operand must be a number.", file=sys.stderr)
                exit(70)
            return -1 * value
        else:
            return not value


class BinaryExpression(Expression):
    def __init__(self, operator: Token, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.left} {self.right})"

    def evaluate(self, env):
        left_value = self.left.evaluate(env)
        right_value = self.right.evaluate(env)

        if self.operator.type == "PLUS":
            if not isinstance(left_value, (float, str)) or not isinstance(right_value, (float, str)) or type(left_value) != type(right_value):
                print("Operands must be two numbers or two strings.", file=sys.stderr)
                exit(70)
            return left_value + right_value
        if self.operator.type == "MINUS":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value - right_value
        # Handle other operators like STAR, SLASH, etc. ...

        # Add more operator checks here...

        return None


class AssignmentExpression(Expression):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def __str__(self) -> str:
        return f"(assignment {self.name} {self.expression})"

    def evaluate(self, env):
        value = self.expression.evaluate(env)
        env.assign(self.name, value)
        return value


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse_primary(self):
        token = self.tokens[self.current]
        if token.type == "TRUE":
            self.current += 1
            return LiteralExpression(True)
        if token.type == "FALSE":
            self.current += 1
            return LiteralExpression(False)
        if token.type == "NIL":
            self.current += 1
            return LiteralExpression(None)
        if token.type in ["NUMBER", "STRING"]:
            self.current += 1
            return LiteralExpression(token.literal)
        if token.type == "LEFT_PAREN":
            self.current += 1
            expression = self.parse_expression()
            self.consume("RIGHT_PAREN")
            return GroupExpression(expression)
        if token.type == "IDENTIFIER":
            self.current += 1
            return VariableExpression(token.lexeme)
        print(f"Unexpected token: {token.lexeme}", file=sys.stderr)
        exit(70)

    def parse_assignment(self):
        expression = self.parse_expression()

        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            if token.type == "EQUAL":
                self.current += 1
                right = self.parse_expression()
                if isinstance(expression, VariableExpression):
                    return AssignmentExpression(expression.name, right)

        return expression

    def parse_expression(self):
        return self.parse_assignment()

    def parse_statements(self):
        statements = []
        while self.tokens[self.current].type != "EOF":
            statement = self.parse_statement()
            statements.append(statement)
        return statements

    def parse_statement(self):
        token = self.tokens[self.current]
        if token.type == "PRINT":
            self.current += 1
            expression = self.parse_expression()
            self.consume("SEMICOLON")
            return PrintStatement(expression)

        if token.type == "VAR":
            self.current += 1
            identifier = self.consume("IDENTIFIER")
            expression = None
            if self.current < len(self.tokens) and self.tokens[self.current].type == "EQUAL":
                self.current += 1
                expression = self.parse_expression()
            self.consume("SEMICOLON")
            return VariableDeclarationStatement(identifier.lexeme, expression)

        if token.type == "LEFT_BRACE":
            self.current += 1
            return BlockStatement(self.parse_block())

        expression = self.parse_expression()
        self.consume("SEMICOLON")
        return ExpressionStatement(expression)

    def parse_block(self):
        statements = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != "RIGHT_BRACE":
            statements.append(self.parse_statement())
        self.consume("RIGHT_BRACE")
        return statements

    def consume(self, type):
        if self.current < len(self.tokens) and self.tokens[self.current].type == type:
            self.current += 1
            return self.tokens[self.current - 1]
        print(f"Expected {type}, found {self.tokens[self.current].type}", file=sys.stderr)
        exit(70)


class Statement(ABC):
    @abstractmethod
    def execute(self, env): pass


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self, env):
        print(lox_representation(self.expression.evaluate(env)))


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def execute(self, env):
        self.expression.evaluate(env)


class VariableDeclarationStatement(Statement):
    def __init__(self, name: str, expression: Expression | None):
        self.expression = expression
        self.name = name

    def execute(self, env):
        if self.expression is None:
            env.define(self.name, None)
        else:
            env.define(self.name, self.expression.evaluate(env))


class BlockStatement(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def execute(self, env):
        local_env = Environment(env)  # Create a new nested environment
        for statement in self.statements:
            statement.execute(local_env)


def lox_representation(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "nil"
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        return value
    return str(value)


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "tokenize":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            for token in tokens:
                print(token)
            if had_error:
                exit(65)
            return

    if command == "parse":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error:
                exit(65)
            expression = Parser(tokens).parse_expression()
            print(expression)
            return

    if command == "evaluate":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error: exit(65)
            expression = Parser(tokens).parse_expression()
            print(lox_representation(expression.evaluate(Environment())))
            return

    if command == "run":
        with open(filename) as file:
            file_contents = file.read()
            tokens, had_error = Scanner(file_contents).scan()
            if had_error: exit(65)
            statements = Parser(tokens).parse_statements()
            env = Environment()
            for statement in statements:
                statement.execute(env)
            return

    print(f"Unknown command: {command}", file=sys.stderr)
    exit(1)


if __name__ == "__main__":
    main()
