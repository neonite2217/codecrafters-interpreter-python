from app.tokenizer import Tokenizer, Token

def is_bool(expr: Token):

    return expr.identifier == "TRUE" or expr.identifier == "FALSE"

def is_nil(expr: Token):

    return expr.identifier == "NIL"

class Parser:

    def __init__(self, contents: str):

        self.tokenizer = Tokenizer(contents)

    def parse_expr(self, expr: Token):

        if is_bool(expr):

            return expr.lexeme

        elif is_nil(expr):

            return expr.lexeme

        else:

            return "error"

    def parse(self):

        return self.parse_expr(self.tokenizer.next_token())
