from enum import Enum, auto
from typing import Optional, List

class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    LEFT_PARENTHESIS = auto()
    RIGHT_PARENTHESIS = auto()
    LEFT_CURLY = auto()
    RIGHT_CURLY = auto()
    ASSIGN = auto()
    PLUS = auto()
    DASH = auto()
    SLASH = auto()
    ASTERISK = auto()
    MODULUS = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EQUAL = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    KEYWORD_FN = auto()
    KEYWORD_LET = auto()
    KEYWORD_IF = auto()
    KEYWORD_ELSEIF = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_RETURN = auto()

class Token:
    def __init__(self, type: TokenType, literal: Optional[str]=None):
        self.type = type
        self.literal = literal

    def __repr__(self) -> str:
        if self.literal is not None:
            return f'{self.type} | \'{self.literal}\''
        else:
            return str(self.type)

class IllegalLexemeError(Exception):
    pass

class Lexer:
    def __init__(self, source: str):
        self.input = source
        self.index = -1
        self.curr = '\0'

    def advance(self) -> bool:
        if self.index + 1 < len(self.input):
            self.index += 1
            self.curr = self.input[self.index]
            return True
        else:
            return False
    
    def peek(self, count: int=1) -> Optional[str]:
        if self.index + count < len(self.input) and self.index + count >= 0:
            return self.input[self.index + count]
        else:
            return None
    
    def read_identifier(self) -> str:
        ident = self.curr
        while (peek := self.peek()) is not None and (peek.isalnum() or peek == '_'):
            ident += peek
            self.advance()
        return ident

    def read_number(self) -> str:
        number = self.curr
        while (peek := self.peek()) is not None and (peek.isdigit() or peek == '.'):
            number += peek
            self.advance()
        try:
            float(number)
        except ValueError:
            raise IllegalLexemeError(number)
        return number
    
    def read_string(self) -> str:
        string = ''
        malformed = True
        while self.advance():
            malformed = False # ugly hack? maybe
            if self.curr == '"':
                break
            string += self.curr
        if self.curr != '"' or malformed:
            raise IllegalLexemeError(f'"{string}')
        return string

    def next_token(self) -> Optional[Token]:
        if not self.advance():
            return None
        while self.curr.isspace():
            if not self.advance():
                return None
        match self.curr:
            case '(':
                return Token(TokenType.LEFT_PARENTHESIS)
            case ')':
                return Token(TokenType.RIGHT_PARENTHESIS)
            case '{':
                return Token(TokenType.LEFT_CURLY)
            case '}':
                return Token(TokenType.RIGHT_CURLY)
            case '+':
                return Token(TokenType.PLUS)
            case '-':
                return Token(TokenType.DASH)
            case '*':
                return Token(TokenType.ASTERISK)
            case '/':
                return Token(TokenType.SLASH)
            case '%':
                return Token(TokenType.MODULUS)
            case ',':
                return Token(TokenType.COMMA)
            case ';':
                return Token(TokenType.SEMICOLON)
            case '"':
                return Token(TokenType.STRING, self.read_string())
            case '=' if self.peek() == '=':
                self.advance()
                return Token(TokenType.EQUAL)
            case '=':
                return Token(TokenType.ASSIGN)
            case '!' if self.peek() == '=':
                self.advance()
                return Token(TokenType.BANG_EQUAL)
            case '!':
                return Token(TokenType.BANG)
            case '<' if self.peek() == '=':
                self.advance()
                return Token(TokenType.LESS_EQUAL)
            case '<':
                return Token(TokenType.LESS)
            case '>' if self.peek() == '=':
                self.advance()
                return Token(TokenType.GREATER_EQUAL)
            case '>':
                return Token(TokenType.GREATER)
            case '&' if self.peek() == '&':
                self.advance()
                return Token(TokenType.AND)
            case '|' if self.peek() == '|':
                self.advance()
                return Token(TokenType.OR)
            case ident if ident.isalpha():
                ident = self.read_identifier()
                match ident:
                    case 'true' | 'false':
                        return Token(TokenType.BOOL, ident)
                    case 'if':
                        return Token(TokenType.KEYWORD_IF)
                    case 'elseif':
                        return Token(TokenType.KEYWORD_ELSEIF)
                    case 'else':
                        return Token(TokenType.KEYWORD_ELSE)
                    case 'return':
                        return Token(TokenType.KEYWORD_RETURN)
                    case 'fn':
                        return Token(TokenType.KEYWORD_FN)
                    case 'let':
                        return Token(TokenType.KEYWORD_LET)
                    case _:
                        return Token(TokenType.IDENTIFIER, ident)
            case number if number.isdigit() or number == '.':
                return Token(TokenType.NUMBER, self.read_number())
            case illegal:
                raise IllegalLexemeError(illegal)

    
    def build_tokens(self) -> List[Token]:
        tokens = []
        while (token := self.next_token()) is not None:
            tokens.append(token)
        return tokens