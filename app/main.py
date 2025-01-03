from abc import ABC, abstractmethod
import sys

class Token:
    def __init__(self, type, lexeme, literal):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal

    def __repr__(self) -> str:
        return f"{self.type} {self.lexeme} {'null' if self.literal is None else self.literal}"

ENVIRONMENT = {}

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
            if char == "(":
                tokens.append(Token("LEFT_PAREN", "(", None))
            elif char == ")":
                tokens.append(Token("RIGHT_PAREN", ")", None))
            elif char == "{":
                tokens.append(Token("LEFT_BRACE", "{", None))
            elif char == "}":
                tokens.append(Token("RIGHT_BRACE", "}", None))
            elif char == "*":
                tokens.append(Token("STAR", "*", None))
            elif char == ".":
                tokens.append(Token("DOT", ".", None))
            elif char == ",":
                tokens.append(Token("COMMA", ",", None))
            elif char == "+":
                tokens.append(Token("PLUS", "+", None))
            elif char == "-":
                tokens.append(Token("MINUS", "-", None))
            elif char == ";":
                tokens.append(Token("SEMICOLON", ";", None))
            elif char == "/":
                if self.current < len(self.source_code) and self.source_code[self.current] == "/":
                    while self.current < len(self.source_code) and self.source_code[self.current] != "\n":
                        self.current += 1
                else:
                    tokens.append(Token("SLASH", "/", None))
            elif char == "=":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("EQUAL_EQUAL", "==", None))
                    self.current += 1
                else:
                    tokens.append(Token("EQUAL", "=", None))
            elif char == "!":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("BANG_EQUAL", "!=", None))
                    self.current += 1
                else:
                    tokens.append(Token("BANG", "!", None))
            elif char == "<":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("LESS_EQUAL", "<=", None))
                    self.current += 1
                else:
                    tokens.append(Token("LESS", "<", None))
            elif char == ">":
                if self.current < len(self.source_code) and self.source_code[self.current] == "=":
                    tokens.append(Token("GREATER_EQUAL", ">=", None))
                    self.current += 1
                else:
                    tokens.append(Token("GREATER", ">", None))
            elif char == "\"":
                string_start = self.current
                while self.current < len(self.source_code) and self.source_code[self.current] != '"':
                    self.current += 1
                if self.current >= len(self.source_code):
                    print(f"[line {self.line}] Error: Unterminated string.", file=sys.stderr)
                    self.had_error = True
                    continue
                self.current += 1
                string_end = self.current - 1
                string_literal = self.source_code[string_start:string_end]
                tokens.append(Token("STRING", f'"{string_literal}"', string_literal))
            elif char.isdigit():
                number_start = self.current - 1
                while self.current < len(self.source_code) and (self.source_code[self.current].isdigit() or self.source_code[self.current] == "."):
                    self.current += 1
                number_end = self.current
                number_literal = self.source_code[number_start:number_end]
                tokens.append(Token("NUMBER", number_literal, float(number_literal)))
            elif char.isalpha() or char == "_":
                identifier_start = self.current - 1
                while self.current < len(self.source_code) and (self.source_code[self.current].isalnum() or self.source_code[self.current] == "_"):
                    self.current += 1
                identifier_end = self.current
                identifier_literal = self.source_code[identifier_start:identifier_end]
                if identifier_literal in ["and", "class", "else", "false", "for", "fun", "if", "nil", "or", "print", "return", "super", "this", "true", "var", "while"]:
                    tokens.append(Token(identifier_literal.upper(), identifier_literal, None))
                else:
                    tokens.append(Token("IDENTIFIER", identifier_literal, None))
            elif char == " ":
                pass
            elif char == "\t":
                pass
            elif char == "\r":
                pass
            elif char == "\f":
                pass
            elif char == "\n":
                self.line += 1
            else:
                print(f"[line {self.line}] Error: Unexpected character: {char}", file=sys.stderr)
                self.had_error = True
        tokens.append(Token("EOF", "", None))
        return tokens, self.had_error

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
        if self.name not in ENVIRONMENT:
            print(f"Undefined variable '{self.name}'", file=sys.stderr)
            exit(70)
        return ENVIRONMENT[self.name]

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

class Interpreter:
    def __init__(self):
        self.had_error = False

    def interpret(self, statement):
        if isinstance(statement, Expression):
            return statement.evaluate()
        return None

def run_interpreter(source_code):
    scanner = Scanner(source_code)
    tokens, had_error = scanner.scan()
    if had_error:
        return
    interpreter = Interpreter()

    for token in tokens:
        if token.type == "EOF":
            break
        print(f"Token: {token}")

# Example usage
if __name__ == "__main__":
    code = """
    var a = 2;
    var b = 3;
    print a + b;
    """
    run_interpreter(code)
