from typing import Optional, List, Union, cast
from enum import Enum, auto

import lex

class UnexpectedTokenError(Exception):
    pass

class Node:
    pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class Leaf(Expression):
    class Kind(Enum):
        IDENTIFIER = auto()
        STRING = auto()
        BOOL = auto()
        NUMBER = auto()

    def __init__(self, token: lex.Token):
        token.literal = cast(str, token.literal) # safe
        match token.type:
            case lex.TokenType.IDENTIFIER:
                self.kind = self.Kind.IDENTIFIER
                self.value = token.literal
            case lex.TokenType.STRING:
                self.kind = self.Kind.STRING
                self.value = token.literal
            case lex.TokenType.BOOL:
                self.kind = self.Kind.BOOL
                self.value = token.literal == 'true'
            case lex.TokenType.NUMBER:
                self.kind = self.Kind.NUMBER
                self.value = float(token.literal)
            case _:
                raise UnexpectedTokenError(self.Kind, token)
    
    def __repr__(self) -> str:
        return f'Leaf(EXPR)[Kind: {self.kind}, Value: {self.value}]'

class Let(Statement):
    def __init__(self, identifier: str, value: Expression):
        self.identifier = identifier
        self.value = value

    def __repr__(self) -> str:
        return f'Let(STMT)[Identifier: {self.identifier}, Value: {self.value}]'

class Return(Statement):
    def __init__(self, value: Expression):
        self.value = value

    def __repr__(self) -> str:
        return f'Return(STMT)[Value: {self.value}]'

class Parser:
    def __init__(self, source: List[lex.Token]):
        self.input = source
        self.index = -1
        self.curr = cast(lex.Token, None)

    def advance(self) -> bool:
        if self.index + 1 < len(self.input):
            self.index += 1
            self.curr = self.input[self.index]
            return True
        else:
            return False
    
    def consume(self) -> lex.Token:
        if not self.advance():
            raise UnexpectedTokenError(lex.Token, None)
        return self.curr

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
        if not self.advance() or self.curr.type != type:
            raise UnexpectedTokenError(type, self.curr)
        return self.curr
    
    def parse_expression(self) -> Expression:
        match self.curr.type:
            case lex.TokenType.IDENTIFIER | lex.TokenType.STRING | lex.TokenType.BOOL | lex.TokenType.NUMBER:
                return Leaf(self.curr)
            case illegal:
                raise UnexpectedTokenError(Expression, illegal)

    def parse_statement(self) -> Optional[Statement]:
        if not self.advance():
            return None
        statement = None
        match self.curr.type:
            case lex.TokenType.KEYWORD_RETURN:
                self.consume()
                statement = Return(self.parse_expression())
                self.expect(lex.TokenType.SEMICOLON)
            case lex.TokenType.KEYWORD_LET:
                identifier = cast(str, self.expect(lex.TokenType.IDENTIFIER).literal)
                self.expect(lex.TokenType.ASSIGN)
                self.consume()
                statement = Let(identifier, self.parse_expression())
                self.expect(lex.TokenType.SEMICOLON)
            case illegal:
                raise UnexpectedTokenError(Statement, illegal)
        return statement
    
    def get_tree(self) -> List[Statement]:
        statements = []
        while (statement := self.parse_statement()) is not None:
            statements.append(statement)
        return statements