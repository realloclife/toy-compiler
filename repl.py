import sys

import lex

def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as file:
            source = file.read()
            tokens = lex.Lexer(source).get_tokens()
            for token in tokens:
                print(token)
            raise SystemExit
    while True:
        source = input('> ')
        if source == 'exit':
            raise SystemExit
        tokens = []
        try:
            tokens = lex.Lexer(source).get_tokens()
        except lex.IllegalLexemeError as e:
            print(f'Invalid lexeme \'{e.args[0]}\'')
        for token in tokens:
            print(token)

if __name__ == '__main__':
    main()