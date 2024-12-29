import sys

def main():
    # Check if the correct number of arguments are passed
    if len(sys.argv) < 3:
        print("Usage: python your_program.py tokenize <filename>", file=sys.stderr)
        exit(1)

    # Get command and filename from the arguments
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
    
    # Placeholder for the scanner (to be implemented)
    if file_contents:
        raise NotImplementedError("Scanner not implemented yet")
    else:
        print("EOF null")  # Placeholder, remove when scanner is implemented

if __name__ == "__main__":
    main()
