from typing import List, cast
import parse
import bytecode

class Codegen:
    def __init__(self, tree: List[parse.Statement]):
        self.tree = tree
        self.code = cast(List[bytecode.Instruction], [])
        self.data = cast(List[bytecode.Object], [])
    
    def trasform_function_call(self, branch: parse.FunctionCall):
        for argument in branch.arguments:
            self.transform_expression(argument)
        # TODO
        
    def transform_expression(self, branch: parse.Expression):
        match type(branch):
            case parse.FunctionCall:
                self.trasform_function_call(cast(parse.FunctionCall, branch))
            case _:
                raise ValueError("UNREACHABLE @ codegen/transform_expression")
    
    def transform_return(self, branch: parse.Return):
        if branch.value is not None:
            self.transform_expression(branch.value)
        else:
            self.code.extend([bytecode.Opcode.PUSH, None])
        self.code.append(bytecode.Opcode.RETURN)
    
    def transform_statement(self, branch: parse.Statement):
        match type(branch):
            case parse.Return:
                return self.transform_return(cast(parse.Return, branch))
            case _:
                raise ValueError('UNREACHABLE @ codegen/transform_statement')
    
    def build_bytecode(self) -> bytecode.Bytecode:
        for statement in self.tree:
            self.transform_statement(statement)
        self.code.append(bytecode.Opcode.EXIT)
        self.code.append(0)
        return (self.data, self.code)