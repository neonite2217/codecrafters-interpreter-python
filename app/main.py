= file.read()

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

            print(lox_representation(expression.evaluate()))

            return



    if command == "run":

        with open(filename) as file:

            file_contents = file.read()

            tokens, had_error = Scanner(file_contents).scan()

            if had_error: exit(65)

            statements = Parser(tokens).parse_statements()

            for statement in statements:

                statement.execute()

            return



    print(f"Unknown command: {command}", file=sys.stderr)

    exit(1)

if __name__ == "__main__":

    main()

avatar zippermonkey
Concise
1 comments
2 months ago
avatar thegostisdead
4 comments
3 days ago
avatar foudre24
13 comments
