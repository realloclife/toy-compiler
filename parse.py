from typing import Optional, List

import lex

class UnexpectedTokenError(Exception):
    pass

class Node:
    pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class Parser:
    def __init__(self, source: List[lex.Token]):
        self.input = source
        self.index = -1
        self.curr: lex.Token = None

    def advance(self) -> bool:
        if self.index + 1 < len(self.input):
            self.index += 1
            self.curr = self.input[self.index]
            return True
        else:
            return False

    def peek(self, count: int = 1) -> Optional[lex.Token]:
        if self.index + count < len(self.input) and self.index + count >= 0:
            return self.input[self.index + count]
        else:
            return None
    
    def match(self, type: lex.TokenType) -> Optional[lex.Token]:
        if (peek := self.peek()) is not None and peek.type == type:
            self.advance()
            return peek
        else:
            return None
    
    def expect(self, type: lex.TokenType) -> lex.Token:
        if (peek := self.peek()) is None or peek.type != type:
            raise UnexpectedTokenError(type, peek)
        else:
            return peek