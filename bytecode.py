from typing import Union, Tuple, List, Any
from enum import Enum, auto

class Opcode(Enum):
    EXIT = auto()
    RETURN = auto()
    NOT = auto()
    NEGATE = auto()
    PUSH = auto()
    LOAD = auto()
    STORE = auto()
    CALL = auto()

Instruction = Union[Opcode, Any]
Object = Union[str, bool, float, None]
Bytecode = Tuple[List[Object], List[Instruction]]