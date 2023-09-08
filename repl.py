from typing import List, cast
import sys

import lex
import parse
import codegen

def main():
    # if len(sys.argv) == 2:
    #     with open(sys.argv[1]) as file:
    #         source = file.read()
    #         tokens = cast(List[lex.Token], [])
    #         try:
    #             tokens = lex.Lexer(source).get_tokens()
    #         except lex.IllegalLexemeError as e:
    #             print(f'Invalid lexeme \'{e.args[0]}\'')
    #         for token in tokens:
    #             print(token)
    #         raise SystemExit
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
        code = codegen.Generator(syntax_tree).build_asm()
        print(code)

if __name__ == '__main__':
    main()