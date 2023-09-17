from typing import List, cast
import sys

import lex
import parse

def main():
    while True:
        source = input('> ')
        if source == 'exit':
            raise SystemExit
        tokens = cast(List[lex.Token], None)
        try:
            tokens = lex.Lexer(source).build_tokens()
        except lex.IllegalLexemeError as e:
            print(f'Invalid lexeme \'{e.args[0]}\'')
            continue
        syntax_tree = cast(List[parse.Statement], None)
        try:
            syntax_tree = parse.Parser(tokens).build_tree()
        except parse.UnexpectedTokenError as e:
            print(f'Expected {e.args[0]}, got {e.args[1]} instead')
            continue
        for statement in syntax_tree:
            print(statement)

if __name__ == '__main__':
    main()