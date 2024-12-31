import unittest

from app.scanner import Scanner

from app.parser import Parser

class TestScanner(unittest.TestCase):

    def test_scanner(self):

        test_cases = [

            (

                '"Hello" = ',

                ['STRING "Hello" Hello', "EQUAL = null", "EOF  null"],

                False,

            ),

            (

                '"Hello" = "Hello" && 42 == 42',

                [

                    'STRING "Hello" Hello',

                    "EQUAL = null",

                    'STRING "Hello" Hello',

                    "NUMBER 42 42.0",

                    "EQUAL_EQUAL == null",

                    "NUMBER 42 42.0",

                    "EOF  null",

                ],

                True,

            ),

            ("1234.1234", ["NUMBER 1234.1234 1234.1234", "EOF  null"], False),

            (

                '(5+3) > 7 ; "Success" != "Failure" & 10 >= 5',

                [

                    "LEFT_PAREN ( null",

                    "NUMBER 5 5.0",

                    "PLUS + null",

                    "NUMBER 3 3.0",

                    "RIGHT_PAREN ) null",

                    "GREATER > null",

                    "NUMBER 7 7.0",

                    "SEMICOLON ; null",

                    'STRING "Success" Success',

                    "BANG_EQUAL != null",

                    'STRING "Failure" Failure',

                    "NUMBER 10 10.0",

                    "GREATER_EQUAL >= null",

                    "NUMBER 5 5.0",

                    "EOF  null",

                ],

                True,

            ),

            (

                "foo bar _hello",

                [

                    "IDENTIFIER foo null",

                    "IDENTIFIER bar null",

                    "IDENTIFIER _hello null",

                    "EOF  null",

                ],

                False,

            ),

            (

                "2 + 3",

                ["NUMBER 2 2.0", "PLUS + null", "NUMBER 3 3.0", "EOF  null"],

                False,

            ),

            ("and", ["AND and null", "EOF  null"], False),

        ]

        for source, expected_tokens, has_errors in test_cases:

            with self.subTest(source=source):

                scanner = Scanner(source)

                scanner.scan()

                self.assertEqual(scanner.has_errors(), has_errors)

                self.assertEqual(scanner.tokens_list(), expected_tokens)

    def test_parser(self, source, expected_expressions, has_errors):

        scanner = Scanner(source)

        scanner.scan()

        tokens = scanner.tokens

        parser = Parser(tokens)

        expression = parser.expression()

        self.assertEqual(has_errors, parser.has_errors())

        self.assertEqual(expected_expressions, str(expression))

    def test_parse_literal(self):

        self.test_parser('("foo")', "(group foo)", False)

    def test_unmatched_parenthesis(self):

        self.test_parser('("foo"', "None", True)

    def test_group(self):

        self.test_parser("((true))", "(group (group true))", False)

    def test_empty(self):

        self.test_parser("()", "None", True)

    def test_number(self):

        self.test_parser("62", "62.0", False),

    def test_unary(self):

        self.test_parser("!true", "(! true)", False),

    def test_arithmetic(self):

        self.test_parser("66 * 57 / 88", "(/ (* 66.0 57.0) 88.0)", False),

    def test_arithmetic_2(self):

        self.test_parser(

            "(11 * -30 / (32 * 90))",

            "(group (/ (* 11.0 (- 30.0)) (group (* 32.0 90.0))))",

            False,

        )

    def test_unmatched_binary(self):

        self.test_parser("(57 +)", "None", True)

if __name__ == "__main__":

    unittest.main()
