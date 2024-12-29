import sys

def main():
    # Log message for debugging
    print("Logs from your program will appear here!", file=sys.stderr)

    # Check if correct number of arguments are passed
    if len(sys.argv) < 3:
        print("Usage: python your_program.py tokenize <filename>", file=sys.stderr)
        exit(1)

    # Get command and filename
    command = sys.argv[1]
    filename = sys.argv[2]

    # Check if the command is "tokenize"
    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    # Try to open the file and read its contents
    try:
        with open(filename, 'r') as file:
            file_contents = file.read()
    except FileNotFoundError:
        print(f"File not found: {filename}", file=sys.stderr)
        exit(1)

    # Tokenize the contents
    for c in file_contents:
        if c == "(":
            print("LEFT_PAREN ( null")
        elif c == ")":
            print("RIGHT_PAREN ) null")

    # End of file
    print("EOF null")

if __name__ == "__main__":
    main()
