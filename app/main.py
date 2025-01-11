import sys

from collections import deque

import traceback

debug = False

token_map = {

    "(": "LEFT_PAREN",

    ")": "RIGHT_PAREN",

    "{": "LEFT_BRACE",

    "}": "RIGHT_BRACE",

    "*": "STAR",

    ".": "DOT",

    ",": "COMMA",

    "+": "PLUS",

    "-": "MINUS",

    ";": "SEMICOLON",

    "=": "EQUAL",

    "!": "BANG",

    "!=": "BANG_EQUAL",

    "==": "EQUAL_EQUAL",

    "<=": "LESS_EQUAL",

    "<": "LESS",

    ">": "GREATER",

    ">=": "GREATER_EQUAL",

    "/": "SLASH",

    "//": "COMMENT",

    "and": "AND",

    "class": "CLASS",

    "else": "ELSE",

    "false": "FALSE",

    "for": "FOR",

    "fun": "FUN",

    "if": "IF",

    "nil": "NIL",

    "or": "OR",

    "print": "PRINT",

    "return": "RETURN",

    "super": "SUPER",

    "this": "THIS",

    "true": "TRUE",

    "var": "VAR",

    "while": "WHILE",

}

def convert_primitive_to_str(val):

    if isinstance(val, bool):

        return str(val).lower()

    if val is None:

        return "nil"

    if isinstance(val, float):

        return int(val) if val.is_integer() else val

    return val

def contains_next_token(file_contents, idx, token):

    if idx + len(token) >= len(file_contents):

        return False

    return file_contents[idx : idx + len(token)] == token

def get_string_literal(file_contents, idx):

    assert file_contents[idx] == '"'

    str = '"'

    curr_idx = idx + 1

    while curr_idx < len(file_contents) and file_contents[curr_idx] != '"':

        str += file_contents[curr_idx]

        curr_idx += 1

    if curr_idx < len(file_contents) and file_contents[curr_idx] == '"':

        str += '"'

    return str

def get_number_literal(file_contents, idx):

    num = ""

    curr_idx = idx

    while curr_idx < len(file_contents) and (

        file_contents[curr_idx].isnumeric() or file_contents[curr_idx] == "."

    ):

        num += file_contents[curr_idx]

        curr_idx += 1

    return num

def get_identifier(file_contents, idx):

    identifier = ""

    curr_idx = idx

    while curr_idx < len(file_contents) and (

        file_contents[curr_idx].isalnum() or file_contents[curr_idx] == "_"

    ):

        identifier += file_contents[curr_idx]

        curr_idx += 1

    return identifier

def tokenize_with_list(file_contents):

    tokens = []

    # Uncomment this block to pass the first stage

    is_commenting = False

    idx = 0

    line = 1

    while idx < len(file_contents):

        ch = file_contents[idx]

        if file_contents[idx] == "\n":

            line += 1

            idx += 1

            is_commenting = False

        elif is_commenting:

            idx += 1

        elif file_contents[idx].isnumeric():

            num_literal = get_number_literal(file_contents, idx)

            tokens.append(("NUMBER", num_literal, float(num_literal)))

            idx += len(num_literal)

        elif file_contents[idx] == '"':

            string_literal = get_string_literal(file_contents, idx)

            if string_literal[0] == '"' and string_literal[-1] == '"':

                tokens.append(("STRING", string_literal, string_literal[1:-1]))

            else:

                return None

            idx += len(string_literal)

        elif file_contents[idx] in (" ", "\t"):

            idx += 1

        elif contains_next_token(file_contents, idx, "<|TAB|>"):

            idx += len("<|TAB|>")

        elif contains_next_token(file_contents, idx, "<|SPACE|>"):

            idx += len("<|SPACE|>")

        elif contains_next_token(file_contents, idx, "//"):

            is_commenting = True

            idx += 1

        elif idx + 1 < len(file_contents) and file_contents[idx : idx + 2] in token_map:

            tokens.append(

                (

                    token_map[file_contents[idx : idx + 2]],

                    file_contents[idx : idx + 2],

                    "null",

                )

            )

            idx += 2

        elif ch in token_map:

            tokens.append((token_map[ch], ch, "null"))

            idx += 1

        elif ch.isalpha() or ch == "_":

            word = get_identifier(file_contents, idx)

            if word in token_map:

                tokens.append((token_map[word], word, "null"))

            else:

                tokens.append(("IDENTIFIER", word, "null"))

            idx += len(word)

        else:

            print(f"[line {line}] Error: Unexpected character: {ch}", file=sys.stderr)

            idx += 1

            return None

    return tokens

def is_executable(maybe_executable):

    return (

        isinstance(maybe_executable, Executable)

        or isinstance(maybe_executable, BlockNode)

        or isinstance(maybe_executable, VariableNode)

        or isinstance(maybe_executable, ElseIfBlockNode)

    )

class BlockNode:

    def __init__(self, tokens, scope):

        # instead of a list of executables, this should be a list of lexemes that we evaluate and then execute

        self.tokens = tokens

        self.scope = scope

    def execute(self):

        interpreter = Interpreter(self.tokens)

        interpreter.execute_all(self.scope)

        # for executable in interpreter.stack:

        #    if is_executable(executable):

        #        executable.execute()

        """



        for executable in self.executables:

            if is_executable(executable):

                executable.execute(self.scope)

        """

class ElseIfBlockNode:

    def __init__(self, if_nodes, else_statement):

        self.if_nodes = if_nodes

        self.else_statement = else_statement

    def execute(self):

        for if_node in self.if_nodes:

            if is_executable(if_node.truth_val):

                if_node.truth_val = if_node.truth_val.execute()

            if if_node.truth_val:

                if_node.block.execute()

                return

        self.else_statement.execute()

class IfNode:

    def __init__(self, truth_val, block):

        self.truth_val = truth_val

        self.block = block

class ElseNode:

    def __init__(self, block):

        self.block = block

class Executable:

    def __init__(self, command, value, value_two=None):

        self.command = command

        self.value = value

        self.value_two = value_two

    def execute(self, scope=None):

        if self.command == "print":

            if is_executable(self.value):

                self.value = self.value.execute()

            print(convert_primitive_to_str(self.value))

            return None

        elif self.command == "if":

            if is_executable(self.value):

                self.value = self.value.execute()

            if self.value:

                self.value_two.execute()

        elif self.command == "=":

            if is_executable(self.value_two):

                self.value_two = self.value_two.execute()

            self.value.var_val = self.value_two

            return self.value_two

    def __repr__(self):

        return f"({self.command} {self.value})"

class VariableNode:

    def __init__(self, var_name, var_val):

        self.var_name = var_name

        self.var_val = var_val

    def execute(self, scope=None):

        if isinstance(self.var_val, VariableNode):

            return self.var_val.execute()

        return self.var_val

class VariableMap:

    # used to manage scopes

    def __init__(self, parent=None):

        self.var_map = {}

        self.parent = parent

    def get_var_map(self):

        return self.var_map

    def variable_exists(self, var_name):

        if self.parent is None:

            return var_name in self.var_map

        if var_name in self.var_map:

            return True

        return self.parent.variable_exists(var_name)

    def get_variable(self, var_name):

        if self.parent is None:

            return self.var_map[var_name]

        if var_name in self.var_map:

            return self.var_map[var_name]

        return self.parent.get_variable(var_name)

    def init_variable(self, var_name, var_node):

        self.var_map[var_name] = var_node

    def set_variable(self, var_name, var_node):

        print(var_name, var_node)

        if self.parent is None:

            assert var_name in self.var_map

            self.var_map[var_name] = var_node

        if var_name in self.var_map:

            self.var_map[var_name] = var_node

        else:

            self.parent.set_variable(var_name, var_node)

class Interpreter:

    def __init__(self, tokens):

        self.tokens = tokens

        self.idx = 0

        self.stack = []

        self.processing_add_minus = False

        self.is_comparing = False

        self.is_defining = False

    def execute_all(self, scope=None):

        var_map = VariableMap() if scope is None else scope

        while self.idx < len(self.tokens):

            self.evaluate_next(var_map)

            if not self.stack:

                continue

            while self.stack[-1] == ";":

                self.stack.pop()

            res = self.stack.pop()

            if is_executable(res) and not isinstance(res, VariableNode):

                self.stack.append(res.execute())

            else:

                self.stack.append(res)

    def evaluate_all(self, var_map=None):

        if var_map is None:

            var_map = VariableMap()

        while self.idx < len(self.tokens):

            self.evaluate_next(var_map)

    def evaluate_next(self, var_map, auto_execute=True):

        # print(self.stack)

        token, word, value = self.tokens[self.idx]

        if debug:

            print(self.stack)

            print(token)

        if token in ("NIL", "FALSE", "TRUE"):

            self.idx += 1

            if token == "NIL":

                self.stack.append(None)

            elif token == "FALSE":

                self.stack.append(False)

            elif token == "TRUE":

                self.stack.append(True)

        if token == "NUMBER":

            self.idx += 1

            self.stack.append(int(value) if value.is_integer() else value)

            if (

                (self.processing_add_minus or self.is_comparing)

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR")

            ):

                self.evaluate_next(var_map, auto_execute)

        if token == "STRING":

            self.idx += 1

            self.stack.append(value)

        if token == "LEFT_PAREN":

            self.idx += 1

            self.match(")", var_map)

            self.stack.append(self.stack.pop())

            if (

                (self.processing_add_minus or self.is_comparing or self.is_defining)

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR", "MINUS", "PLUS")

            ):

                self.evaluate_next(var_map, auto_execute)

        if token == "RIGHT_PAREN":

            self.idx += 1

            self.stack.append(")")

        if token == "BANG":

            self.idx += 1

            self.evaluate_next(var_map, auto_execute)

            res = self.stack.pop()

            if is_executable(res):

                res = res.execute()

            return_val = not res

            self.stack.append(return_val)

        if token == "MINUS":

            if len(self.stack) > 0:

                self.processing_add_minus = True

                self.evaluate_binary("-", var_map)

                self.processing_add_minus = False

            else:

                self.idx += 1

                self.evaluate_next(var_map, auto_execute)

                unary_val = self.stack.pop()

                if isinstance(unary_val, bool):

                    raise Exception("Operand must be a number, not bool.")

                if not isinstance(unary_val, float) and not isinstance(unary_val, int):

                    raise Exception("Operand must be a number.")

                return_val = -1 * unary_val

                self.stack.append(return_val)

        if token == "STAR":

            self.evaluate_binary("*", var_map)

            if (

                self.is_comparing

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR", "MINUS", "PLUS")

            ):

                self.evaluate_next(var_map, auto_execute)

        if token == "SLASH":

            self.evaluate_binary("/", var_map)

            if (

                self.is_comparing

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR", "MINUS", "PLUS")

            ):

                self.evaluate_next(var_map, auto_execute)

        if token == "PLUS":

            self.processing_add_minus = True

            self.evaluate_binary("+", var_map)

            if (

                self.is_comparing

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR", "MINUS", "PLUS")

            ):

                self.evaluate_next(var_map, auto_execute)

            self.processing_add_minus = False

        if token == "LESS":

            self.is_comparing = True

            self.evaluate_binary("<", var_map)

            self.is_comparing = False

        if token == "GREATER":

            self.is_comparing = True

            self.evaluate_binary(">", var_map)

            self.is_comparing = False

        if token == "GREATER_EQUAL":

            self.is_comparing = True

            self.evaluate_binary(">=", var_map)

            self.is_comparing = False

        if token == "LESS_EQUAL":

            self.is_comparing = True

            self.evaluate_binary("<=", var_map)

            self.is_comparing = False

        if token == "EQUAL":

            if self.is_defining:

                self.idx += 1

                self.stack.append("=")

            else:

                self.idx += 1

                left = self.stack.pop()

                token = self.match_multiple([";", ")"], var_map)

                right = self.stack.pop()

                if isinstance(right, VariableNode):

                    right = right.execute()

                self.stack.append(Executable("=", left, right))

                # left.var_val = right

                # self.stack.append(right)

                self.stack.append(token)

        if token == "EQUAL_EQUAL":

            self.is_comparing = True

            self.evaluate_binary("==", var_map)

            self.is_comparing = False

        if token == "BANG_EQUAL":

            self.is_comparing = True

            self.evaluate_binary("!=", var_map)

            self.is_comparing = False

        if token == "SEMICOLON":

            self.idx += 1

            self.is_defining = False

            self.stack.append(";")

        if token == "PRINT":

            self.idx += 1

            self.match(";", var_map)

            unary_val = self.stack.pop()

            self.stack.append(";")

            if isinstance(unary_val, VariableNode):

                unary_val = unary_val.execute()

            self.stack.append(Executable("print", unary_val))

        if token == "VAR":

            self.is_defining = True

            self.idx += 1

            self.evaluate_next(var_map, auto_execute)

            var_name = self.stack.pop()

            self.evaluate_next(var_map, auto_execute)

            if self.stack[-1] == ";":

                self.stack.pop()

                var_node = VariableNode(var_name, None)

                var_map.init_variable(var_name, var_node)

                return

            assert self.stack.pop() == "="

            self.is_defining = False

            try:

                self.evaluate_next(var_map, auto_execute)

                while self.stack[-1] != ";":

                    self.evaluate_next(var_map, auto_execute)

            except IndexError:

                raise Exception("[line 1] expect close")

            self.stack.pop()

            var_val = self.stack.pop() if self.stack else None

            var_node = VariableNode(var_name, var_val)

            var_map.init_variable(var_name, var_node)

        if token == "IDENTIFIER":

            self.idx += 1

            if not self.is_defining and not var_map.variable_exists(word):

                raise Exception("undefined var")

            if self.is_defining:

                self.stack.append(word)

            else:

                self.stack.append(var_map.get_variable(word))

        if token == "RIGHT_BRACE":

            self.idx += 1

            self.stack.append("}")

        if token == "LEFT_BRACE":

            self.idx += 1

            block_tokens = []

            braces = ["{"]

            next_var_map = VariableMap(var_map)

            while braces:

                next_token, next_word, _ = self.tokens[self.idx]

                if next_token == "LEFT_BRACE":

                    braces.append("{")

                elif next_token == "RIGHT_BRACE":

                    braces.pop()

                block_tokens.append(self.tokens[self.idx])

                self.idx += 1

            # popping off the right brace

            assert block_tokens.pop()[0] == "RIGHT_BRACE", "not right brace"

            block_node = BlockNode(block_tokens, next_var_map)

            if auto_execute:

                block_node.execute()

            else:

                self.stack.append(block_node)

        if token == "IF":

            self.idx += 1

            self.evaluate_next(var_map, auto_execute)

            truth_val = self.stack.pop()

            self.evaluate_next(var_map, auto_execute=False)

            executable = self.stack.pop()

            if self.idx >= len(self.tokens) or (

                self.idx < len(self.tokens) and self.tokens[self.idx][0] != "ELSE"

            ):

                self.stack.append(Executable("if", truth_val, executable))

                return

            self.evaluate_next(var_map, auto_execute)

            else_if_block = self.stack.pop()

            self.stack.append(

                ElseIfBlockNode(

                    [IfNode(truth_val, executable)] + else_if_block.if_nodes,

                    else_if_block.else_statement,

                )

            )

        if token == "ELSE":

            self.idx += 1

            self.evaluate_next(var_map, auto_execute=False)

            executable = self.stack.pop()

            self.stack.append(ElseIfBlockNode([], executable))

        if token == "OR":

            self.evaluate_binary("or", var_map)

        if token == "AND":

            self.evaluate_binary("and", var_map)

        return None

    def match(self, symbol, var_map):

        self.evaluate_next(var_map)

        try:

            while self.stack[-1] != symbol:

                self.evaluate_next(var_map)

        except IndexError:

            raise Exception(f"[line 1] expect {symbol}")

        self.stack.pop()

    def match_multiple(self, symbols, var_map):

        self.evaluate_next(var_map)

        try:

            while self.stack[-1] not in symbols:

                self.evaluate_next(var_map)

        except IndexError:

            raise Exception(f"[line 1] expect {symbols}")

        return self.stack.pop()

    def is_numeric_literal(self, val):

        if isinstance(val, bool):

            return False

        return isinstance(val, int) or isinstance(val, float)

    def is_str_literal(self, val):

        return isinstance(val, str)

    def evaluate_binary(self, symbol, var_map):

        self.idx += 1

        left_val = self.stack.pop()

        self.evaluate_next(var_map)

        right_val = self.stack.pop()

        if is_executable(left_val):

            left_val = left_val.execute()

        if left_val and symbol == "or":

            self.stack.append(left_val)

            return

        if not left_val and symbol == "and":

            self.stack.append(False)

            return

        if is_executable(right_val):

            right_val = right_val.execute()

        if symbol == "*":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val * right_val

        elif symbol == "/":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val / right_val

            return_val = (

                int(return_val)

                if isinstance(return_val, float) and return_val.is_integer()

                else return_val

            )

        elif symbol == "-":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val - right_val

        elif symbol == "+":

            if not (

                (self.is_str_literal(left_val) and self.is_str_literal(right_val))

                or (

                    self.is_numeric_literal(left_val)

                    and self.is_numeric_literal(right_val)

                )

            ):

                raise Exception("Operand must be both number or strings.")

            return_val = left_val + right_val

        elif symbol == ">":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val > right_val

        elif symbol == "<":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val < right_val

        elif symbol == "<=":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val <= right_val

        elif symbol == ">=":

            if not self.is_numeric_literal(left_val) or not self.is_numeric_literal(

                right_val

            ):

                raise Exception("Operand must be a number.")

            return_val = left_val >= right_val

        elif symbol == "==":

            return_val = left_val == right_val

        elif symbol == "!=":

            return_val = left_val != right_val

        elif symbol == "or":

            return_val = left_val or right_val

        elif symbol == "and":

            return_val = left_val and right_val

        else:

            return_val = None

        self.stack.append(return_val)

class Parser:

    def __init__(self, tokens):

        self.tokens = tokens

        self.idx = 0

        self.stack = []

        self.evaluating_stack = []

        self.processing_add_minus = False

        self.is_defining = False

    def parse_all(self):

        while self.idx < len(self.tokens):

            self.parse_next()

    def match(self, symbol, err_msg=""):

        self.parse_next()

        try:

            while self.stack[-1] != symbol:

                self.parse_next()

        except Exception as e:

            if not err_msg:

                raise e

            else:

                raise Exception(err_msg)

        self.stack.pop()

    def match_multiple(self, symbols, err_msg=""):

        self.parse_next()

        try:

            while self.stack[-1] not in symbols:

                self.parse_next()

        except Exception as e:

            if not err_msg:

                raise e

            else:

                raise Exception(err_msg)

        return self.stack.pop()

    def parse_next(self):

        token, word, value = self.tokens[self.idx]

        if debug:

            print(self.stack)

            print(token)

        # print(self.stack)

        # print(token)

        if token in ("NIL", "FALSE", "TRUE"):

            self.idx += 1

            self.stack.append(word)

        if token == "NUMBER":

            self.idx += 1

            self.stack.append(value)

            if (

                self.processing_add_minus

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR")

            ):

                self.parse_next()

        if token == "STRING":

            self.idx += 1

            self.stack.append(value)

        if token == "LEFT_PAREN":

            self.idx += 1

            self.match(")")

            value = f"(group {self.stack.pop()})"

            self.stack.append(value)

            if (

                (self.processing_add_minus or self.is_defining)

                and self.idx < len(self.tokens)

                and self.tokens[self.idx][0] in ("SLASH", "STAR", "MINUS", "PLUS")

            ):

                self.parse_next()

        if token == "RIGHT_PAREN":

            self.idx += 1

            self.stack.append(")")

        if token == "BANG":

            self.idx += 1

            self.parse_next()

            return_val = f"(! {self.stack.pop()})"

            self.stack.append(return_val)

        if token == "MINUS":

            if len(self.stack) > 0:

                self.processing_add_minus = True

                self.parse_binary("-")

                self.processing_add_minus = False

            else:

                self.idx += 1

                self.parse_next()

                return_val = f"(- {self.stack.pop()})"

                self.stack.append(return_val)

        if token == "STAR":

            self.parse_binary("*")

        if token == "SLASH":

            self.parse_binary("/")

        if token == "PLUS":

            self.processing_add_minus = True

            self.parse_binary("+")

            self.processing_add_minus = False

        if token == "EQUAL":

            if self.is_defining:

                self.idx += 1

                self.stack.append("=")

            else:

                self.idx += 1

                left = self.stack.pop()

                popped_token = self.match_multiple([";", ")"])

                right = self.stack.pop()

                self.stack.append(f"(= {left} {right})")

                self.stack.append(popped_token)

        if token == "LESS":

            self.parse_binary("<")

        if token == "GREATER":

            self.parse_binary(">")

        if token == "GREATER_EQUAL":

            self.parse_binary(">=")

        if token == "LESS_EQUAL":

            self.parse_binary("<=")

        if token == "EQUAL_EQUAL":

            self.parse_binary("==")

        if token == "BANG_EQUAL":

            self.parse_binary("!=")

        if token == "SEMICOLON":

            self.is_defining = False

            self.idx += 1

            self.stack.append(";")

        if token == "PRINT":

            self.idx += 1

            self.parse_next()

            try:

                while self.stack[-1] != ";":

                    self.parse_next()

            except IndexError:

                raise Exception("[line 1] expect close")

            self.stack.pop()

            val = self.stack.pop()

            self.stack.append(f"(print {val})")

        if token == "VAR":

            self.is_defining = True

            self.idx += 1

            self.parse_next()

            var_name = self.stack.pop()

            self.parse_next()

            if self.stack[-1] == ";":

                self.stack.pop()

                self.stack.append(f"(var {var_name} nil)")

                return

            assert self.stack.pop() == "="

            self.is_defining = False

            try:

                self.parse_next()

                while self.stack[-1] != ";":

                    self.parse_next()

            except IndexError:

                raise Exception("[line 1] expect close")

            self.stack.pop()

            var_val = self.stack.pop()

            self.stack.append(f"(var {var_name} {var_val})")

        if token == "IDENTIFIER":

            self.idx += 1

            self.stack.append("var_" + word)

        if token == "RIGHT_BRACE":

            self.idx += 1

            self.stack.append("}")

        if token == "LEFT_BRACE":

            self.idx += 1

            self.stack.append("{")

            self.match("}")

            executables = []

            while self.stack[-1] != "{":

                executables.append(self.stack.pop())

            executables.reverse()

            self.stack.pop()

            self.stack.append(f'(block {" ".join(executables)})')

        if token == "IF":

            self.idx += 1

            self.parse_next()

            truth_val = self.stack.pop()

            self.parse_next()

            executable = self.stack.pop()

            if self.idx >= len(self.tokens) or (

                self.idx < len(self.tokens) and self.tokens[self.idx][0] != "ELSE"

            ):

                self.stack.append(f"(if {truth_val} {executable})")

                return

            self.parse_next()

            else_if_block = self.stack.pop()

            self.stack.append(f"(if {truth_val} {executable} {else_if_block})")

        if token == "ELSE":

            self.idx += 1

            self.parse_next()

            executable = self.stack.pop()

            if self.idx >= len(self.tokens) or (

                self.idx < len(self.tokens) and self.tokens[self.idx][0] != "IF"

            ):

                self.stack.append(f"(else {executable})")

                return

            self.parse_next()

        if token == "OR":

            self.parse_binary("or")

        if token == "AND":

            self.parse_binary("and")

        return None

    def parse_binary(self, symbol):

        self.idx += 1

        left_val = self.stack.pop()

        self.parse_next()

        right_val = self.stack.pop()

        return_val = f"({symbol} {left_val} {right_val})"

        self.stack.append(return_val)

def parse(file_contents):

    tokens = tokenize_with_list(file_contents)

    if tokens is None:

        return 65

    parser = Parser(tokens)

    try:

        parser.parse_all()

    except Exception as e:

        # print(str(e))

        return 65

    for eval in parser.stack:

        print(eval)

    return 0

def evaluate(file_contents):

    tokens = tokenize_with_list(file_contents)

    if tokens is None:

        return 65

    interpreter = Interpreter(tokens)

    try:

        interpreter.evaluate_all()

    except Exception as e:

        return 70

    for value in interpreter.stack:

        print(convert_primitive_to_str(value))

    return 0

def run(file_contents):

    tokens = tokenize_with_list(file_contents)

    if tokens is None:

        return 65

    parser = Parser(tokens)

    if debug:

        print("PARSING")

    try:

        parser.parse_all()

    except Exception as e:

        if debug:

            print("PARSER")

            print(e)

        return 65

    if debug:

        print(parser.stack)

    interpreter = Interpreter(tokens)

    if debug:

        print("INTERPRETING")

    try:

        interpreter.execute_all()

    except Exception as e:

        if debug:

            print("INTERPRETER ERROR")

            traceback.print_exc()

            print(e)

        return 70

    """

    has_runtime_error = False

    if debug:

        print("INTERPRETING")

    try:

        interpreter.evaluate_all()

    except Exception as e:

        if debug:

            print("INTERPRETER")

            print(e)

        has_runtime_error = True

    if debug:

        print("INTERPRETER STACK")

        print(interpreter.stack)

    for value in interpreter.stack:

        if is_executable(value):

            value.execute()

    if has_runtime_error:

        return 70

    """

    return 0

def tokenize(file_contents):

    # Uncomment this block to pass the first stage

    if file_contents:

        has_errors = False

        is_commenting = False

        idx = 0

        line = 1

        while idx < len(file_contents):

            ch = file_contents[idx]

            if file_contents[idx] == "\n":

                line += 1

                idx += 1

                is_commenting = False

            elif is_commenting:

                idx += 1

            elif file_contents[idx].isnumeric():

                num_literal = get_number_literal(file_contents, idx)

                print("NUMBER", num_literal, float(num_literal))

                idx += len(num_literal)

            elif file_contents[idx] == '"':

                string_literal = get_string_literal(file_contents, idx)

                if string_literal[0] == '"' and string_literal[-1] == '"':

                    print("STRING", string_literal, string_literal[1:-1])

                else:

                    print(f"[line {line}] Error: Unterminated string.", file=sys.stderr)

                    has_errors = True

                idx += len(string_literal)

            elif file_contents[idx] in (" ", "\t"):

                idx += 1

            elif contains_next_token(file_contents, idx, "<|TAB|>"):

                idx += len("<|TAB|>")

            elif contains_next_token(file_contents, idx, "<|SPACE|>"):

                idx += len("<|SPACE|>")

            elif contains_next_token(file_contents, idx, "//"):

                is_commenting = True

                idx += 1

            elif (

                idx + 1 < len(file_contents)

                and file_contents[idx : idx + 2] in token_map

            ):

                print(

                    token_map[file_contents[idx : idx + 2]],

                    file_contents[idx : idx + 2],

                    "null",

                )

                idx += 2

            elif ch in token_map:

                print(token_map[ch], ch, "null")

                idx += 1

            elif ch.isalpha() or ch == "_":

                word = get_identifier(file_contents, idx)

                if word in token_map:

                    print(token_map[word], word, "null")

                else:

                    print("IDENTIFIER", word, "null")

                idx += len(word)

            else:

                print(

                    f"[line {line}] Error: Unexpected character: {ch}", file=sys.stderr

                )

                has_errors = True

                idx += 1

        print("EOF  null")

        if has_errors:

            return 65

        else:

            return 0

    else:

        print(

            "EOF  null"

        )  # Placeholder, remove this line when implementing the scanner

        return 0

def main():

    if len(sys.argv) < 3:

        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)

        exit(1)

    command = sys.argv[1]

    filename = sys.argv[2]

    with open(filename) as file:

        file_contents = file.read()

    print("Logs from your program will appear here!", file=sys.stderr)

    if command == "tokenize":

        return tokenize(file_contents)

    elif command == "parse":

        return parse(file_contents)

    elif command == "evaluate":

        return evaluate(file_contents)

    elif command == "run":

        return run(file_contents)

    else:

        print(f"Unknown command: {command}", file=sys.stderr)

        exit(1)

if __name__ == "__main__":

    exit(main())
