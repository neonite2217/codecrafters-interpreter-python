from app.tokenizer import Token, TokenType

from app.parser import Parser, ParserError

import pytest

# (5 - (3 - 1)) + -1

# // expect: (+ (group (- 5.0 (group (- 3.0 1.0)))) (- 1.0))

class TestPrint:

    def test_print_token(self, capfd):

        print(Token(TokenType.FALSE, "to_be_printed", "dont_print"), end="")

        print(Token(TokenType.TRUE, "to_be_printed", "dont_print"), end="")

        print(Token(TokenType.NIL, "to_be_printed", "dont_print"), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == 3 * "to_be_printed"

    @pytest.mark.parametrize(

        "token, expected_stdout",

        [

            (Token(TokenType.NUMBER, "5", "5.0"), "5.0"),

            (Token(TokenType.NUMBER, "79.20", "79.2"), "79.2"),

        ],

    )

    def test_print_number_literal(self, capfd, token, expected_stdout):

        print(token, end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == expected_stdout

    def test_string_literal(self, capfd):

        print(Token.create_string_literal("hello"), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "hello"  # without quotes, so not '"hello"'

class TestGrouping:

    def test_double_parenthesis(self, capfd):

        tokens = [

            Token(TokenType.LEFT_PAREN, "(", "null"),

            Token(TokenType.LEFT_PAREN, "(", "null"),

            Token(TokenType.TRUE, "true", "true"),

            Token(TokenType.RIGHT_PAREN, ")", "null"),

            Token(TokenType.RIGHT_PAREN, ")", "null"),

        ]

        print(Parser(tokens)._parse_primary(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(group (group true))"

    def test_empty_group(self):

        tokens = [

            Token(TokenType.LEFT_PAREN, "(", "null"),

            Token(TokenType.RIGHT_PAREN, ")", "null"),

        ]

        with pytest.raises(ParserError) as e:

            Parser(tokens)._parse_primary()

class TestUnary:

    def test_negation(self, capfd):

        tokens = [

            Token(TokenType.MINUS, "-", "null"),

            Token(TokenType.NUMBER, "5", "5.0"),

        ]

        print(Parser(tokens)._parse_unary(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(- 5.0)"

    def test_logical_not(self, capfd):

        tokens = [

            Token(TokenType.BANG, "!", "null"),

            Token(TokenType.TRUE, "true", "null"),

        ]

        print(Parser(tokens)._parse_unary(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(! true)"

    def test_nested_logical_not(self, capfd):

        tokens = [

            Token(TokenType.BANG, "!", "null"),

            Token(TokenType.BANG, "!", "null"),

            Token(TokenType.TRUE, "true", "null"),

        ]

        print(Parser(tokens)._parse_unary(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(! (! true))"

    def test_combined_with_groupping(self, capfd):

        tokens = [

            Token(TokenType.BANG, "!", "null"),

            Token(TokenType.LEFT_PAREN, "(", "null"),

            Token(TokenType.TRUE, "true", "null"),

            Token(TokenType.RIGHT_PAREN, ")", "null"),

        ]

        print(Parser(tokens)._parse_unary(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(! (group true))"

class TestFactor:

    def test_multiplication(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.STAR, "*", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_factor(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(* 5.0 2.0)"

    def test_division(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.SLASH, "/", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_factor(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(/ 5.0 2.0)"

    def test_division_with_multiplication(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.SLASH, "/", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

            Token(TokenType.STAR, "*", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_factor(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(* (/ 5.0 2.0) 2.0)"

class TestTerm:

    def test_addition(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.PLUS, "+", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_term(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(+ 5.0 2.0)"

    def test_subtraction(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.PLUS, "-", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_term(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(- 5.0 2.0)"

class TestComparison:

    def test_single_comparison(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.GREATER, ">", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_comparison(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(> 5.0 2.0)"

    def test_multiple_comparison(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "83", "83.0"),

            Token(TokenType.LESS, "<", "null"),

            Token(TokenType.NUMBER, "99", "99.0"),

            Token(TokenType.LESS, "<", "null"),

            Token(TokenType.NUMBER, "115", "115.0"),

        ]

        print(Parser(tokens)._parse_comparison(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(< (< 83.0 99.0) 115.0)"

class TestEquality:

    def test_single_equality(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "5", "5.0"),

            Token(TokenType.EQUAL_EQUAL, "==", "null"),

            Token(TokenType.NUMBER, "2", "2.0"),

        ]

        print(Parser(tokens)._parse_equality(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(== 5.0 2.0)"

    def test_multiple_equality(self, capfd):

        tokens = [

            Token(TokenType.NUMBER, "83", "83.0"),

            Token(TokenType.BANG_EQUAL, "!=", "null"),

            Token(TokenType.NUMBER, "99", "99.0"),

            Token(TokenType.EQUAL_EQUAL, "==", "null"),

            Token(TokenType.NUMBER, "115", "115.0"),

        ]

        print(Parser(tokens)._parse_equality(), end="")

        captured_print = capfd.readouterr()

        assert captured_print.out == "(== (!= 83.0 99.0) 115.0)"

class TestSyntacticError:

    def test_missing_right_operand(self):

        tokens = [

            Token(TokenType.LEFT_PAREN, "(", "null"),

            Token(TokenType.NUMBER, "72", "72.0"),

            Token(TokenType.PLUS, "+", "null"),

        ]

        with pytest.raises(ParserError) as e:

            Parser(tokens).parse()
