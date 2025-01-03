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
        self.values = {}
        self.parent = parent

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

ENVIRONMENT = Environment()  # Global environment

class Scanner:
    # (same as before)

class Expression(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def evaluate(self):
        pass

class LiteralExpression(Expression):
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.value is True: return "true"
        if self.value is False: return "false"
        if self.value is None: return "nil"
        return f"{self.value}"

    def evaluate(self):
        return self.value

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self):
        return ENVIRONMENT.get(self.name)

    def __str__(self) -> str:
        return f"(identifier {self.name})"

class GroupExpression(Expression):
    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def __str__(self) -> str:
        return f"(group {self.expression})"

    def evaluate(self):
        return self.expression.evaluate()

class UnaryExpression(Expression):
    def __init__(self, operator: Token, expression: Expression) -> None:
        self.operator = operator
        self.expression = expression

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.expression})"

    def evaluate(self):
        value = self.expression.evaluate()
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

    def evaluate(self):
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()

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

        if self.operator.type == "STAR":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value * right_value

        if self.operator.type == "SLASH":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value / right_value

        if self.operator.type == "BANG_EQUAL":
            return left_value != right_value

        if self.operator.type == "EQUAL_EQUAL":
            return left_value == right_value

        if self.operator.type == "GREATER":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value > right_value

        if self.operator.type == "GREATER_EQUAL":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value >= right_value

        if self.operator.type == "LESS":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value < right_value

        if self.operator.type == "LESS_EQUAL":
            if not isinstance(left_value, float) or not isinstance(right_value, float):
                print("Operands must be numbers.", file=sys.stderr)
                exit(70)
            return left_value <= right_value

class AssignmentExpression(Expression):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def __str__(self) -> str:
        return f"(assignment {self.name} {self.expression})"

    def evaluate(self):
        value = self.expression.evaluate()
        ENVIRONMENT.assign(self.name, value)
        return value

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse_primary(self):
        self.current += 1
        token = self.tokens[self.current - 1]

        if token.type == "TRUE":
            return LiteralExpression(True)

        if token.type == "FALSE":
            return LiteralExpression(False)

        if token.type == "NIL":
            return LiteralExpression(None)

        if token.type in ["NUMBER", "STRING"]:
            return LiteralExpression(token.literal)

        if token.type == "LEFT_PAREN":
            expression = self.parse_expression()
            self.consume("RIGHT_PAREN")
            return GroupExpression(expression)

        if token.type == "IDENTIFIER":
            return VariableExpression(token.lexeme)

        print(f"Error at {token.lexeme}: Expect expression.", file=sys.stderr)
        exit(65)

    def parse_assignment(self):
        expression = self.parse_equality()

        if self.current < len(self.tokens):
            token = self.tokens[self.current]

            if token.type == "EQUAL":
                self.current += 1
                if isinstance(expression, VariableExpression):
                    right = self.parse_assignment()
                    return AssignmentExpression(expression.name, right)

        return expression

    def parse_block(self):
        statements = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != "RIGHT_BRACE":
            statements.append(self.parse_statement())

        self.consume("RIGHT_BRACE")
        return statements

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

            if self.tokens[self.current].type == "EQUAL":
                self.current += 1
                expression = self.parse_expression()
                self.consume("SEMICOLON")
                return VariableDeclarationStatement(identifier.lexeme, expression)

            self.consume("SEMICOLON")
            return VariableDeclarationStatement(identifier.lexeme, None)

        if token.type == "LEFT_BRACE":
            self.current += 1
            return BlockStatement(self.parse_block())

        return self.parse_expression()

    def parse_expression(self):
        # parsing logic...
        pass


class Interpreter:
    def interpret(self, expression):
        if isinstance(expression, Expression):
            return expression.evaluate()

    def execute_statements(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, statement):
        # execute logic...
        pass

def run_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    scanner = Scanner(content)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse_statements()
    interpreter = Interpreter()
    interpreter.execute_statements(statements)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 interpreter.py <script>")
        sys.exit(64)

    script = sys.argv[1]
    run_file(script)

if __name__ == "__main__":
    main()
