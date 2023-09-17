# TODO remove __repr__ after the parser is complete

from typing import Optional, List, Dict, Callable, Union, Tuple, cast
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

PrefixParser = Callable[[], Expression]
InfixParser = Callable[[Expression], Expression]

class Precedence(Enum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    LOGICAL = auto()
    PREFIX = auto()
    CALL = auto()

class Identifier(Expression):
    def __init__(self, value: str):
        self.value = value
    
    def __repr__(self) -> str:
        return f'Identifier(EXPR)[Value: {self.value}]'

class Leaf(Expression):
    class Kind(Enum):
        IDENTIFIER = auto()
        STRING = auto()
        BOOL = auto()
        NUMBER = auto()

    def __init__(self, token: lex.Token):
        self.value = cast(Union[str, bool, float], None)
        token.literal = cast(str, token.literal) # safe
        match token.type:
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

class Unary(Expression):
    class Operation(Enum):
        NOT = auto()
        NEGATE = auto()
    
    def __init__(self, operation: Operation, value: Expression):
        self.operation = operation
        self.value = value
    
    def __repr__(self) -> str:
        return f'Unary(EXPR)[Operation: {self.operation}, Value: {self.value}]'

class Binary(Expression):
    class Operation(Enum):
        ADD = auto()
        SUBTRACT = auto()
        MULTIPLY = auto()
        DIVIDE = auto()
        MODULO = auto()
        LESS = auto()
        GREATER = auto()
        LESS_EQUAL = auto()
        GREATER_EQUAL = auto()
        EQUAL = auto()
        NOT_EQUAL = auto()
        AND = auto()
        OR = auto()
    
    def __init__(self, left: Expression, operation: Operation, right: Expression):
        self.left = left
        self.operation = operation
        self.right = right

    def __repr__(self) -> str:
        return f'Binary(EXPR)[Left: {self.left}, Operation: {self.operation}, Right: {self.right}]'

class Block(Expression):
    def __init__(self, body: List[Statement]):
        self.body = body
    
    def __repr__(self) -> str:
        return f'Block(EXPR)[Body: ({", ".join(str(stmt) for stmt in self.body)})]'

class FunctionCall(Expression):
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

    def __repr__(self) -> str:
        return f'FunctionCall(STMT)[Name: {self.name}, Arguments: ({", ".join(str(arg) for arg in self.arguments)})]'

class If(Statement):
    def __init__(self, main: Tuple[Expression, Block], alternatives: Dict[Expression, Block]={}, fallback: Optional[Block]=None):
        self.main = main
        self.alternatives = alternatives
        self.fallback = fallback
    
    def __repr__(self) -> str:
        if len(self.alternatives) > 0:
            if self.fallback is not None:
                return f'If(STMT)[Main: {self.main}, Alternatives: {self.alternatives}, Fallback: {self.fallback}]'
            else:
                return f'If(STMT)[Main: {self.main}, Alternatives: {self.alternatives}]'
        else:
            if self.fallback is not None:
                return f'If(STMT)[Main: {self.main}, Fallback: {self.fallback}]'
            else:
                return f'If(STMT)[Main: {self.main}]'

class FunctionDef(Statement):
    def __init__(self, name: str, arguments: List[str], body: Block):
        self.name = name
        self.arguments = arguments
        self.body = body
    
    def __repr__(self) -> str:
        return f'FunctionDef(STMT)[Name: {self.name}, Arguments: ({", ".join(self.arguments)}), Body: {self.body}]'

class Wrapper(Statement):
    def __init__(self, value: Expression):
        self.value = value
    
    def __repr__(self) -> str:
        return f'Wrapper(STMT)[Value: {self.value}]'

class Let(Statement):
    def __init__(self, identifier: str, value: Expression):
        self.identifier = identifier
        self.value = value

    def __repr__(self) -> str:
        return f'Let(STMT)[Identifier: {self.identifier}, Value: {self.value}]'

class Return(Statement):
    def __init__(self, value: Optional[Expression]=None):
        self.value = value

    def __repr__(self) -> str:
        if self.value is not None:
            return f'Return(STMT)[Value: {self.value}]'
        else:
            return 'Return(STMT)[]'

class Parser:
    def __init__(self, source: List[lex.Token]):
        self.input = source
        self.index = -1
        self.curr = cast(lex.Token, None)
        self.prefix_parsers: Dict[lex.TokenType, PrefixParser] = {
            lex.TokenType.IDENTIFIER: self.parse_identifier,
            lex.TokenType.STRING: self.parse_leaf,
            lex.TokenType.BOOL: self.parse_leaf,
            lex.TokenType.NUMBER: self.parse_leaf,
            lex.TokenType.BANG: self.parse_unary,
            lex.TokenType.DASH: self.parse_unary,
            lex.TokenType.LEFT_PARENTHESIS: self.parse_grouped,
            lex.TokenType.LEFT_CURLY: self.parse_block,
        }
        self.infix_parsers: Dict[lex.TokenType, InfixParser] = {
            lex.TokenType.PLUS: self.parse_binary,
            lex.TokenType.DASH: self.parse_binary,
            lex.TokenType.ASTERISK: self.parse_binary,
            lex.TokenType.SLASH: self.parse_binary,
            lex.TokenType.MODULUS: self.parse_binary,
            lex.TokenType.LESS: self.parse_binary,
            lex.TokenType.GREATER: self.parse_binary,
            lex.TokenType.LESS_EQUAL: self.parse_binary,
            lex.TokenType.GREATER_EQUAL: self.parse_binary,
            lex.TokenType.EQUAL: self.parse_binary,
            lex.TokenType.BANG_EQUAL: self.parse_binary,
            lex.TokenType.AND: self.parse_binary,
            lex.TokenType.OR: self.parse_binary,
            lex.TokenType.LEFT_PARENTHESIS: self.parse_fn_call,
        }
        self.infix_precedences = {
            lex.TokenType.EQUAL: Precedence.EQUALS,
            lex.TokenType.BANG_EQUAL: Precedence.EQUALS,
            lex.TokenType.LESS: Precedence.LESSGREATER,
            lex.TokenType.GREATER: Precedence.LESSGREATER,
            lex.TokenType.LESS_EQUAL: Precedence.LESSGREATER,
            lex.TokenType.GREATER_EQUAL: Precedence.LESSGREATER,
            lex.TokenType.PLUS: Precedence.SUM,
            lex.TokenType.DASH: Precedence.SUM,
            lex.TokenType.SLASH: Precedence.PRODUCT,
            lex.TokenType.ASTERISK: Precedence.PRODUCT,
            lex.TokenType.MODULUS: Precedence.PRODUCT,
            lex.TokenType.AND: Precedence.LOGICAL,
            lex.TokenType.OR: Precedence.LOGICAL,
            lex.TokenType.LEFT_PARENTHESIS: Precedence.CALL,
        }

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

    def peek(self, count: int=1) -> Optional[lex.Token]:
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
    
    def expect_current(self, type: lex.TokenType) -> lex.Token:
        if self.curr.type != type:
            raise UnexpectedTokenError(type, self.curr)
        return self.curr
    
    def expect(self, type: lex.TokenType) -> lex.Token:
        if not self.advance() or self.curr.type != type:
            raise UnexpectedTokenError(type, self.curr)
        return self.curr
    
    def get_current_precedence(self) -> Precedence:
        if (prec := self.infix_precedences.get(self.curr.type)) is not None:
            return prec
        return Precedence.LOWEST

    def get_peek_precedence(self) -> Precedence:
        if (peek := self.peek()) is not None and (prec := self.infix_precedences.get(peek.type)) is not None:
            return prec
        return Precedence.LOWEST
    
    def parse_expression(self, precedence: Precedence=Precedence.LOWEST) -> Expression:
        prefix = self.prefix_parsers.get(self.curr.type)
        if prefix is None:
            raise UnexpectedTokenError(Expression, self.curr)
        left = prefix()
        while True:
            if (peek := self.peek()) is None or peek.type == lex.TokenType.SEMICOLON or precedence.value >= self.get_peek_precedence().value:
                break
            infix = self.infix_parsers.get(peek.type)
            if infix is None:
                break
            self.consume()
            left = infix(left)
        return left
    
    def parse_identifier(self) -> Identifier:
        return Identifier(cast(str, self.curr.literal))
    
    def parse_leaf(self) -> Leaf:
        return Leaf(self.curr)
    
    def parse_unary(self) -> Unary:
        operation = None
        match self.curr.type:
            case lex.TokenType.BANG:
                operation = Unary.Operation.NOT
            case lex.TokenType.DASH:
                operation = Unary.Operation.NEGATE
            case _:
                raise ValueError(f'UNREACHABLE [{self.curr}] @ Parser.parse_unary')
        self.consume()
        return Unary(operation, self.parse_expression(Precedence.PREFIX))
    
    def parse_binary(self, left: Expression) -> Binary:
        operation = None
        match self.curr.type:
            case lex.TokenType.PLUS:
                operation = Binary.Operation.ADD
            case lex.TokenType.DASH:
                operation = Binary.Operation.SUBTRACT
            case lex.TokenType.ASTERISK:
                operation = Binary.Operation.MULTIPLY
            case lex.TokenType.SLASH:
                operation = Binary.Operation.DIVIDE
            case lex.TokenType.MODULUS:
                operation = Binary.Operation.MODULO
            case lex.TokenType.LESS:
                operation = Binary.Operation.LESS
            case lex.TokenType.GREATER:
                operation = Binary.Operation.GREATER
            case lex.TokenType.LESS_EQUAL:
                operation = Binary.Operation.LESS_EQUAL
            case lex.TokenType.GREATER_EQUAL:
                operation = Binary.Operation.GREATER_EQUAL
            case lex.TokenType.EQUAL:
                operation = Binary.Operation.EQUAL
            case lex.TokenType.BANG_EQUAL:
                operation = Binary.Operation.NOT_EQUAL
            case lex.TokenType.AND:
                operation = Binary.Operation.AND
            case lex.TokenType.OR:
                operation = Binary.Operation.OR
            case _:
                raise ValueError(f'UNREACHABLE [{self.curr}] @ Parser.parse_binary')
        precedence = self.get_current_precedence()
        self.consume()
        right = self.parse_expression(precedence)
        return Binary(left, operation, right)
    
    def parse_grouped(self) -> Expression:
        self.consume()
        expression = self.parse_expression()
        self.expect(lex.TokenType.RIGHT_PARENTHESIS)
        return expression
    
    def parse_block(self) -> Block:
        statements = []
        while True:
            if self.consume().type == lex.TokenType.RIGHT_CURLY:
                break
            if (stmt := self.parse_statement()) is None:
                raise UnexpectedTokenError(Statement, None)
            statements.append(stmt)
        return Block(statements)

    def parse_fn_call(self, left: Expression) -> FunctionCall:
        args = []
        self.consume()
        while self.curr.type != lex.TokenType.RIGHT_PARENTHESIS:
            args.append(self.parse_expression(Precedence.LOWEST))
            if not self.match(lex.TokenType.COMMA):
                self.expect(lex.TokenType.RIGHT_PARENTHESIS)
                break
            self.expect_current(lex.TokenType.COMMA)
            self.consume()
        self.expect_current(lex.TokenType.RIGHT_PARENTHESIS)
        return FunctionCall(cast(Identifier, left).value, args)

    def parse_statement(self) -> Optional[Statement]:
        match self.curr.type:
            case lex.TokenType.KEYWORD_IF: return self.parse_if()
            case lex.TokenType.KEYWORD_RETURN: return self.parse_return()
            case lex.TokenType.KEYWORD_LET: return self.parse_let()
            case lex.TokenType.KEYWORD_FN: return self.parse_fn_def()
            case _: return self.parse_wrapper()
    
    def parse_fn_def(self) -> FunctionDef:
        name = cast(str, self.expect(lex.TokenType.IDENTIFIER).literal)
        self.expect(lex.TokenType.LEFT_PARENTHESIS)
        args = []
        self.consume()
        while self.curr.type != lex.TokenType.RIGHT_PARENTHESIS:
            args.append(cast(str, self.expect_current(lex.TokenType.IDENTIFIER).literal))
            if not self.match(lex.TokenType.COMMA):
                self.expect(lex.TokenType.RIGHT_PARENTHESIS)
                break
            self.expect_current(lex.TokenType.COMMA)
            self.consume()
        self.expect(lex.TokenType.LEFT_CURLY)
        body = self.parse_block()
        self.expect(lex.TokenType.SEMICOLON)
        return FunctionDef(name, args, body)

    def parse_if(self) -> If:
        self.consume()
        condition = self.parse_expression()
        self.expect(lex.TokenType.LEFT_CURLY)
        consequence = self.parse_block()
        main = (condition, consequence)
        alternatives = {}
        fallback = None
        self.consume()
        while self.curr.type == lex.TokenType.KEYWORD_ELSEIF:
            self.consume()
            condition = self.parse_expression()
            self.expect(lex.TokenType.LEFT_CURLY)
            consequence = self.parse_block()
            alternatives[condition] = consequence
            self.consume()
        if self.curr.type == lex.TokenType.KEYWORD_ELSE:
            self.expect(lex.TokenType.LEFT_CURLY)
            fallback = self.parse_block()
            self.consume()
        self.expect_current(lex.TokenType.SEMICOLON)
        return If(main, alternatives, fallback)

    def parse_return(self) -> Return:
        if self.match(lex.TokenType.SEMICOLON):
            return Return()
        self.consume()
        statement = Return(self.parse_expression())
        self.expect(lex.TokenType.SEMICOLON)
        return statement
    
    def parse_let(self) -> Let:
        identifier = cast(str, self.expect(lex.TokenType.IDENTIFIER).literal)
        self.expect(lex.TokenType.ASSIGN)
        self.consume()
        statement = Let(identifier, self.parse_expression())
        self.expect(lex.TokenType.SEMICOLON)
        return statement
    
    def parse_wrapper(self) -> Wrapper:
        statement = Wrapper(self.parse_expression())
        self.expect(lex.TokenType.SEMICOLON)
        return statement
    
    def build_tree(self) -> List[Statement]:
        statements = []
        if not self.advance():
            return []
        while (statement := self.parse_statement()) is not None:
            statements.append(statement)
            if not self.advance():
                return statements
        return statements