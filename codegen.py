from typing import List, Optional, Union, cast
from enum import Enum, auto

import parse

class Generator:
    def __init__(self, syntax_tree: List[parse.Statement]):
        self.syntax_tree = syntax_tree
        self.instructions = cast(str, '')
        self.stack_offset = 0
    
    def add_instruction(self, instruction: str):
        self.instructions += instruction
        self.instructions += '\n'
    
    def add_prologue(self):
        self.add_instruction('push rbp')
        self.add_instruction('mov rbp, rsp')
        self.add_instruction('sub esp, 256')
    
    def add_epilogue(self):
        self.add_instruction('mov eax, 0')
        self.add_instruction('leave')
        self.add_instruction('ret')
    
    def generate_expression(self, expression: parse.Expression):
        match expression:
            case parse.Leaf(kind=parse.Leaf.Kind.BOOL, value=bool_value):
                self.stack_offset += 1
                self.add_instruction(f'mov BYTE PTR [ebp-{self.stack_offset}], {int(bool_value)}')
            case parse.Binary(left=left_expr, operation=parse.Binary.Operation.EQUAL, right=right_expr):
                self.generate_expression(left_expr)
                self.generate_expression(right_expr)
                self.add_instruction(f'movzx eax, BYTE PTR [ebp-{self.stack_offset - 1}]')
                self.add_instruction(f'cmp al, BYTE PTR [ebp-{self.stack_offset}]')
                self.add_instruction('sete al')
                self.add_instruction(f'mov BYTE PTR [ebp-{self.stack_offset + 1}], al')
            case _:
                raise ValueError('UNIMPLEMENTED [{statement}] @ Generator.generate_expression')

    def build_asm(self) -> str:
        self.add_prologue()
        for statement in self.syntax_tree:
            match statement:
                case parse.Wrapper(value=wrapper_value):
                    self.generate_expression(wrapper_value)
                case _:
                    raise ValueError('UNIMPLEMENTED [{statement}] @ Generator.build_ir')
        self.add_epilogue()
        return self.instructions